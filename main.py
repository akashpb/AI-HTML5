from flask import Flask, render_template, send_file, request
from expr import *
from graphviz import Source
from random import randrange
from utils import *

app = Flask(__name__)
filename = ''
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

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/bdd')
def bdd():
	return render_template("bdd.html")

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
