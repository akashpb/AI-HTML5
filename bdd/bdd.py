from pyeda.inter import *
from graphviz import Source
from flask import send_file

def bdd_img():
	a, b, c = map(bddvar, 'abc')
	f = a & b | a & c | b & c
	gv = Source(f.to_dot())
	gv.format = "png"
	gv.render('render_img_name')
