from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def main():
    return 'Hello, World!'

@app.route('/bdd')
def bdd():
	render_template("rough.html")

@app.route('/proplog')
def proplog():
	return render_template("proplog.html")

# if __name__ == '__main__':
# 	app.run(debug=True)
