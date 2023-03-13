from flask import Flask, make_response, render_template, request, redirect
from hashlib import sha256
import os
import uuid
from secret import email, password, salt

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    # checks whether user is logged in arld
    if request.cookies.get("user"):
        cookie = request.cookies.get("user")
        cookies = []
        with open("db/sessions", "r") as f:
            for i in f.read().splitlines():
                data = i.split(" ")
                cookies.append(data)
        for a in cookies:
            if cookie == a[1]:
                return redirect("/users/" + a[0])
    # logs in if username and password is correct
    if request.method == "POST":
        username = request.form["username"].strip()
        password = str(sha256(str(request.form["password"].strip() + salt).encode("utf-8")).hexdigest())
        data = []
        with open("db/users", "r") as f:
            for i in f.read().splitlines():
                data.append(i.split(" "))
        for d in data:
            if username == d[0] and password == d[1]:
                cookie = str(uuid.uuid4())
                with open("db/sessions", "a") as f:
                    f.write("\n" + username + " " + cookie)
                resp = make_response(redirect("/users/" + username))
                resp.set_cookie("user", cookie)
                return resp
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    # checks whether user is logged in arld
    if request.cookies.get("user"):
        cookie = request.cookies.get("user")
        cookies = []
        with open("db/sessions", "r") as f:
            for i in f.read().splitlines():
                data = i.split(" ")
                cookies.append(data)
        for a in cookies:
            if cookie == a[1]:
                return redirect("/" + a[0])
    if request.method == "POST":
        cookie = str(uuid.uuid4())
        with open("users", "a") as f:
            f.write(cookie + " ")
        resp = make_response(redirect("/" + cookie))
        resp.set_cookie("user", cookie)
        return resp
    else:
        return render_template("login.html")


@app.errorhandler(404)
def page_not_found(e):
    return "this page doesnt exist", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)