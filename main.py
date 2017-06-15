from flask import Flask, render_template, send_file, request
from pyeda.inter import *
from graphviz import Source
from random import randrange

# from bdd import bdd

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
	filename = str(gv.render('bdd_img'))
	print(filename)

@app.route('/')
def main():
    return 'Hello, World!'

@app.route('/bdd')
def bdd():
	return render_template("bdd.html")

@app.route('/get_image', methods = ['GET'])
def get_image():
	exp = str(request.args.get("expr"))
	exp = exp.replace("*", "&")
	print(exp)
	bdd_img(exp)
	return send_file(filename, mimetype='image/png')

@app.route('/proplog')
def proplog():
	return render_template("proplog.html")

if __name__ == '__main__':
	app.run(debug=True)
