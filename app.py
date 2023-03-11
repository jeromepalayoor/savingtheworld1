from flask import Flask, render_template
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return "pls login"

@app.route('/register')
def register():
    return "registering"

@app.errorhandler(404)
def page_not_found(e):
    return "this page doesnt exist", 404

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)