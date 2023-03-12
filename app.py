from flask import Flask, make_response, render_template, request, redirect
from hashlib import sha256
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.cookies.get('user'):
        cookie = request.cookies.get('user')
        cookies = []
        with open('db/users', 'r') as f:
            for i in f.read().split(' '):
                cookies.append(i)
        if cookie in cookies:
            return redirect('/' + cookie)
    if request.method == 'POST':
        cookie = str(uuid.uuid4())
        with open('db/users', 'a') as f:
            f.write(cookie + ' ')
        resp = make_response(redirect('/' + cookie))
        resp.set_cookie('user', cookie)
        return resp
    else:
        return render_template('login.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.cookies.get('user'):
        cookie = request.cookies.get('user')
        cookies = []
        with open('users', 'r') as f:
            for i in f.read().split(' '):
                cookies.append(i)
        if cookie in cookies:
            return redirect('/' + cookie)
    if request.method == 'POST':
        cookie = str(uuid.uuid4())
        with open('users', 'a') as f:
            f.write(cookie + ' ')
        resp = make_response(redirect('/' + cookie))
        resp.set_cookie('user', cookie)
        return resp
    else:
        return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return "this page doesnt exist", 404

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)