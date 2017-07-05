"""
The :mod:`pyeda.boolalg.bdd` module implements
Boolean functions represented as binary decision diagrams.
Interface Functions:
* :func:`bddvar` --- Return a unique BDD variable
* :func:`expr2bdd` --- Convert an expression into a binary decision diagram
* :func:`bdd2expr` --- Convert a binary decision diagram into an expression
* :func:`upoint2bddpoint` --- Convert an untyped point into a BDD point
* :func:`ite` --- BDD if-then-else operator
Interface Classes:
* :class:`BDDNode`
* :class:`BinaryDecisionDiagram`
  * :class:`BDDConstant`
  * :class:`BDDVariable`
"""

import collections
import random
import weakref

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import exprvar, Or, And
from pyeda.util import cached_property


# existing BDDVariable references
_VARS = dict()

# node/bdd cache
_NODES = weakref.WeakValueDictionary()
_BDDS = weakref.WeakValueDictionary()


class BDDNode:
	"""Binary decision diagram node
	A BDD node represents one cofactor in the decomposition of a Boolean
	function.
	Nodes are uniquely identified by a ``root`` integer,
	``lo`` child node, and ``hi`` child node:
	* ``root`` is the cofactor variable's ``uniqid`` attribute
	* ``lo`` is the zero cofactor node
	* ``hi`` is the one cofactor node
	The ``root`` of the zero node is -1,
	and the ``root`` of the one node is -2.
	Both zero/one nodes have ``lo=None`` and ``hi=None``.
	Do **NOT** create BDD nodes using the ``BDDNode`` constructor.
	BDD node instances are managed internally.
	"""
	def __init__(self, root, lo, hi):
		# print("Class BDDNode")
		self.root = root
		self.lo = lo
		self.hi = hi


BDDNODEZERO = _NODES[(-1, None, None)] = BDDNode(-1, None, None)
BDDNODEONE = _NODES[(-2, None, None)] = BDDNode(-2, None, None)


def bddvar(name, index=None):
	# print("bddvar")
	r"""Return a unique BDD variable.
	A Boolean *variable* is an abstract numerical quantity that may assume any
	value in the set :math:`B = \{0, 1\}`.
	The ``bddvar`` function returns a unique Boolean variable instance
	represented by a binary decision diagram.
	Variable instances may be used to symbolically construct larger BDDs.
	A variable is defined by one or more *names*,
	and zero or more *indices*.
	Multiple names establish hierarchical namespaces,
	and multiple indices group several related variables.
	If the ``name`` parameter is a single ``str``,
	it will be converted to ``(name, )``.
	The ``index`` parameter is optional;
	when empty, it will be converted to an empty tuple ``()``.
	If the ``index`` parameter is a single ``int``,
	it will be converted to ``(index, )``.
	Given identical names and indices, the ``bddvar`` function will always
	return the same variable:
	>>> bddvar('a', 0) is bddvar('a', 0)
	True
	To create several single-letter variables:
	>>> a, b, c, d = map(bddvar, 'abcd')
	To create variables with multiple names (inner-most first):
	>>> fifo_push = bddvar(('push', 'fifo'))
	>>> fifo_pop = bddvar(('pop', 'fifo'))
	.. seealso::
	   For creating arrays of variables with incremental indices,
	   use the :func:`pyeda.boolalg.bfarray.bddvars` function.
	"""
	bvar = boolfunc.var(name, index)
	try:
		var = _VARS[bvar.uniqid]
	except KeyError:
		var = _VARS[bvar.uniqid] = BDDVariable(bvar)
		_BDDS[var.node] = var
	return var


def _expr2bddnode(expr):
	"""Convert an expression into a BDD node."""
	# print("_expr2bddnode")
	if expr.is_zero():
		return BDDNODEZERO
	elif expr.is_one():
		return BDDNODEONE
	else:
		top = expr.top

		# Register this variable
		_ = bddvar(top.names, top.indices)

		root = top.uniqid
		lo = _expr2bddnode(expr.restrict({top: 0}))
		hi = _expr2bddnode(expr.restrict({top: 1}))
		return _bddnode(root, lo, hi)


def expr2bdd(expr):
	"""Convert an expression into a binary decision diagram."""
	# print("expr2bdd")
	return _bdd(_expr2bddnode(expr))

def _bddnode(root, lo, hi):
	"""Return a unique BDD node."""
	# print("_bddnode")
	if lo is hi:
		node = lo
	else:
		key = (root, lo, hi)
		try:
			node = _NODES[key]
		except KeyError:
			node = _NODES[key] = BDDNode(*key)
	return node


def _bdd(node):
	"""Return a unique BDD."""
	# print("_bdd")
	try:
		bdd = _BDDS[node]
	except KeyError:
		bdd = _BDDS[node] = BinaryDecisionDiagram(node)
	return bdd


class BinaryDecisionDiagram(boolfunc.Function):
	"""Boolean function represented by a binary decision diagram
	.. seealso::
	   This is a subclass of :class:`pyeda.boolalg.boolfunc.Function`
	BDDs have a single attribute, ``node``,
	that points to a node in the managed unique table.
	There are two ways to construct a BDD:
	* Convert an expression using the ``expr2bdd`` function.
	* Use operators on existing BDDs.
	Use the ``bddvar`` function to create BDD variables,
	and use the Python ``~|&^`` operators for NOT, OR, AND, XOR.
	For example::
	   >>> a, b, c, d = map(bddvar, 'abcd')
	   >>> f = ~a | b & c ^ d
	The ``BinaryDecisionDiagram`` class is useful for type checking,
	e.g. ``isinstance(f, BinaryDecisionDiagram)``.
	Do **NOT** create a BDD using the ``BinaryDecisionDiagram`` constructor.
	BDD instances are managed internally,
	and you will not be able to use the Python ``is`` operator to establish
	formal equivalence with manually constructed BDDs.
	"""
	def __init__(self, node):
		# print("Class BinaryDecisionDiagram")
		self.node = node

	# Operators
	def __invert__(self):
		return _bdd(_neg(self.node))

	def __or__(self, other):
		other_node = self.box(other).node
		# f | g <=> ITE(f, 1, g)
		return _bdd(_ite(self.node, BDDNODEONE, other_node))

	def __and__(self, other):
		other_node = self.box(other).node
		# f & g <=> ITE(f, g, 0)
		return _bdd(_ite(self.node, other_node, BDDNODEZERO))

	def __xor__(self, other):
		other_node = self.box(other).node
		# f ^ g <=> ITE(f, g', g)
		return _bdd(_ite(self.node, _neg(other_node), other_node))

	def __rshift__(self, other):
		other_node = self.box(other).node
		# f => g <=> ITE(f', 1, g)
		return _bdd(_ite(_neg(self.node), BDDNODEONE, other_node))

	def __rrshift__(self, other):
		other_node = self.box(other).node
		# f => g <=> ITE(f', 1, g)
		return _bdd(_ite(_neg(other_node), BDDNODEONE, self.node))

	# Specific to BinaryDecisionDiagram

	def dfs_postorder(self):
		"""Iterate through nodes in depth first search (DFS) post-order."""
		# print("Class BinaryDecisionDiagram _dfs_postorder")
		yield from _dfs_postorder(self.node, set())

	def to_dot(self, name='BDD'): # pragma: no cover
		"""Convert to DOT language representation.
		See the
		`DOT language reference <http://www.graphviz.org/content/dot-language>`_
		for details.
		"""
		# print("to_dot")
		parts = ['graph', name, '{']
		for node in self.dfs_postorder():
			if node is BDDNODEZERO:
				parts += ['n' + str(id(node)), '[label=0,shape=box];']
			elif node is BDDNODEONE:
				parts += ['n' + str(id(node)), '[label=1,shape=box];']
			else:
				v = _VARS[node.root]
				parts.append('n' + str(id(node)))
				parts.append('[label="{}",shape=circle];'.format(v))
		for node in self.dfs_postorder():
			if node is not BDDNODEZERO and node is not BDDNODEONE:
				parts += ['n' + str(id(node)), '--',
						  'n' + str(id(node.lo)),
						  '[label=0,style=dashed];']
				parts += ['n' + str(id(node)), '--',
						  'n' + str(id(node.hi)),
						  '[label=1];']
		parts.append('}')
		return " ".join(parts)


class BDDConstant(BinaryDecisionDiagram):
	"""Binary decision diagram constant zero/one
	The ``BDDConstant`` class is useful for type checking,
	e.g. ``isinstance(f, BDDConstant)``.
	Do **NOT** create a BDD using the ``BDDConstant`` constructor.
	BDD instances are managed internally,
	and the BDD zero/one instances are singletons.
	"""
	def __init__(self, node, value):
		# print("Class BDDConstant")
		super(BDDConstant, self).__init__(node)
		self.value = value

	def __bool__(self):
		return bool(self.value)

	def __int__(self):
		return self.value

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self.value)


BDDZERO = _BDDS[BDDNODEZERO] = BDDConstant(BDDNODEZERO, 0)
BDDONE = _BDDS[BDDNODEONE] = BDDConstant(BDDNODEONE, 1)


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):

	"""Binary decision diagram variable
	The ``BDDVariable`` class is useful for type checking,
	e.g. ``isinstance(f, BDDVariable)``.
	Do **NOT** create a BDD using the ``BDDVariable`` constructor.
	Use the :func:`bddvar` function instead.
	"""
	def __init__(self, bvar):
		# print("Class BDDVariable")
		boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
		node = _bddnode(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
		BinaryDecisionDiagram.__init__(self, node)

def _dfs_postorder(node, visited):
	"""Iterate through nodes in DFS post-order."""
	# print("_dfs_postorder")
	if node.lo is not None:
		yield from _dfs_postorder(node.lo, visited)
	if node.hi is not None:
		yield from _dfs_postorder(node.hi, visited)
	if node not in visited:
		visited.add(node)
		yield node
