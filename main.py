from flask import Flask, render_template, send_file, request
from expr import *
from graphviz import Source
from random import randrange
from utils import *
from dd import autoref as _bdd


app = Flask(__name__)
filename = ''
filename_reorder = ''
filename_reorder_special = ''

def bdd_img(exp):
	# a, b, c = map(bddvar, 'abc')
	# exp = "a & b | a & c | b & c | d"
	print(exp)
	exp = expr(exp)
	f = expr2bdd(exp)

	gv = Source(f.to_dot())
	gv.format = "png"
	# img = gv.render('render_img_name'+ str(randrange(0, 100)))
	global filename
	filename = str(gv.render('../images/bdd_img'))
	print(filename)


def bdd_img_reorder(exp, order):
	bdd = _bdd.BDD()
	bdd.configure(reordering = True)
	order_dict = dict((k.strip(), int(v.strip())) for k,v in 
              (item.split(':') for item in order.split(',')))
	for key, value in order_dict.items():
		bdd.add_var(key)
	u = bdd.add_expr(exp)
	bdd.collect_garbage()
	bdd.dump('../images/bdd_reorder.png')
	global filename_reorder
	filename_reorder = '../images/bdd_reorder.png'

def bdd_img_special_order(exp, order):
	bdd = _bdd.BDD()
	bdd.configure(reordering = True)	
	order_dict = dict((k.strip(), int(v.strip())) for k,v in 
              (item.split(':') for item in order.split(',')))
	for key, value in order_dict.items():
		bdd.add_var(key)
	u = bdd.add_expr(exp)
	print(order_dict)
	print(bdd.vars)
	_bdd.reorder(bdd, order_dict)
	print(bdd.vars)
	bdd.collect_garbage()
	bdd.dump('../images/bdd_reorder_special.png')
	global filename_reorder_special
	filename_reorder_special = '../images/bdd_reorder_special.png'

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/bdd')
def bdd():
	return render_template("bdd.html")

@app.route('/bddreorder')
def bddreorder():
	return render_template("bddreorder.html")

@app.route('/booleanexpr')
def booleanexpr():
	return render_template("booleanexpr.html")

@app.route('/proplog')
def proplog():
	return render_template("proplog.html")

@app.route('/truthtabletobool')
def truthtabletobool():
	return render_template("truthtabletobool.html")

@app.route('/get_robdd_image', methods = ['GET'])
def get_robdd_image():
	exp = str(request.args.get("expr"))
	exp = exp.replace("*", "&")
	print(exp)
	bdd_img(exp)
	return send_file(filename, mimetype='image/png')

@app.route('/get_robdd_reorder_image', methods = ['GET'])
def get_robdd_reorder_image():
	exp = str(request.args.get("expr"))
	order = str(request.args.get("order"))
	exp = exp.replace("*", "&")
	print(exp)
	bdd_img_reorder(exp, order)
	return send_file(filename_reorder, mimetype='image/png')

@app.route('/get_robdd_reorder_special_image', methods = ['GET'])
def get_robdd_reorder_special_image():
	exp = str(request.args.get("expr"))
	order = str(request.args.get("order"))
	exp = exp.replace("*", "&")
	print(exp)
	print(order)
	bdd_img_special_order(exp, order)
	return send_file(filename_reorder_special, mimetype='image/png')

@app.route('/get_min_expr', methods = ['GET'])
def get_min_expr():
	exp = str(request.args.get("expr"))
	exp = exp.replace("*", "&")
	f = expr(exp)
	f1m = espresso_exprs(f.to_dnf())

	return str(f1m)

@app.route('/get_expr_from_tt', methods = ['GET'])
def get_expr_from_tt():
	ttvalues = str(request.args.get("ttvalues"))
	x = int(request.args.get("x"))
	X = ttvars('x', x)
	f = truthtable(X, ttvalues)
	f1m = espresso_tts(f)

	return str(f1m)

if __name__ == '__main__':
	app.run(debug=True)