from dd import autoref as _bdd

bdd = _bdd.BDD()
bits = ('x', 'y', 'z', 'a')
for var in bits:
	bdd.add_var(var)
u = bdd.add_expr('(x & y) | ~z & a')
bdd.collect_garbage()
bdd.dump('awesome.png')