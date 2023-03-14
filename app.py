from flask import Flask, make_response, render_template, redirect, request
from hashlib import sha256
import os
import uuid
from secret import myemail, mypassword, salt
import smtplib
from email.mime.text import MIMEText
import re
import string
import random

alphanumeric = string.ascii_letters + string.digits

app = Flask(__name__)

#home page, to update
@app.route("/")
def home():
    return render_template("index.html")

#send emails to verify account
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "Savingtheworld1 Account Verification"
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

#login handler
@app.route("/login", methods=["POST", "GET"])
def login():
    # checks whether user is logged in arld
    if request.cookies.get("user"):
        cookie = request.cookies.get("user")
        cookies = []
        with open("db/sessions", "r") as f:
            for i in f.read().strip().splitlines():
                data = i.split(",")
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
            for i in f.read().strip().splitlines():
                data.append(i.split(","))
        for d in data:
            if username == d[0] and password == d[1]:
                cookie = str(uuid.uuid4())
                with open("db/sessions", "a") as f:
                    f.write(username + " " + cookie + '\n')
                resp = make_response(redirect("/users/" + username))
                resp.set_cookie("user", cookie)
                return resp
        return make_response(redirect("/error?error=Incorrect username and/or password"))
    else:
        return render_template("login.html")


#register new account
@app.route("/register", methods=["POST", "GET"])
def register():
    # checks whether user is logged in arld
    if request.cookies.get("user"):
        cookie = request.cookies.get("user")
        cookies = []
        with open("db/sessions", "r") as f:
            for i in f.read().strip().splitlines():
                data = i.split(",")
                cookies.append(data)
        for a in cookies:
            if cookie == a[1]:
                return redirect("/" + a[0])
    if request.method == "POST":
        username = request.form["username"].strip().replace("\n", " ").replace(",", " ")
        if not username.isalnum():
            return make_response(redirect("/error?error=Username contains invalid characters"))
        email = request.form["email"].strip().replace("\n", " ").replace(",", " ")
        password = request.form["password"].strip().replace("\n", " ").replace(",", " ")
        if not password.isalnum():
            return make_response(redirect("/error?error=Password contains invalid characters"))
        class_ = request.form["class"].strip().replace("\n", " ").replace(",", " ")
        fullname = request.form["fullname"].strip().replace("\n", " ").replace(",", " ")
        if not re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[-]?\w+[.]\w{2,3}$", email): #check if email is valid using regex
            return make_response(redirect("/error?error=Email is invalid"))
        data = []
        with open("db/users", "r") as f:
            for i in f.read().strip().splitlines():
                data.append(i.split(","))
        for d in data:
            print(d)
            if username == d[0]:
                return make_response(redirect("/error?error=Username is in use already"))
            if email == d[3]:
                return make_response(redirect("/error?error=Email is in use already"))
        with open('db/users', 'a') as f:
            adding = username + ',' + str(sha256(str(password + salt).encode("utf-8")).hexdigest()) + ',' + fullname + ',' + email + ',' + class_ + ',' + 'false' + '\n'
            f.write(adding)
        token = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
        with open("db/verification", "a"):
            f.write(username + "," + token + "\n")
        send_email("Blog account activated", f"Please verify your email before using your account {request.url_root}verify?token={token}", myemail, [email], mypassword)
        cookie = str(uuid.uuid4())
        with open("db/sessions", "a") as f:
            f.write(username + "," + cookie + "\n")
        resp = make_response(redirect("/users/" + username))
        resp.set_cookie("user", cookie)
        return resp
    else:
        return render_template("register.html")

#verify email
@app.route("/verify")
def verify():
    if request.args.get('token'):
        token = request.args.get('token')
        data = []
        with open("db/verification", "r") as f:
            for i in f.read().strip().splitlines():
                data.append(i.split(","))
        for d in data:
            if d[1] == token:
                userdata = []
                with open("db/users", "r") as f:
                    for i in f.read().strip().splitlines():
                        userdata.append(i.split(","))
                for user in userdata:
                    if user[0] == d[0]:
                        user[5] = "True"
                with open("db/users", "w") as f:
                    for user in userdata:
                        f.write(f"{user[0]},{user[1]},{user[2]},{user[3]},{user[4]},{user[5]}\n")
                cookie = str(uuid.uuid4())
                with open("db/sessions", "a") as f:
                    f.write(d[0] + "," + cookie + "\n")
                resp = make_response(redirect("/users/" + d[0]))
                resp.set_cookie("user", cookie)
                return resp
    return render_template("verify.html")

#user page
@app.route("/users/<username>")
def userpage(username):
    data = []
    with open("db/users", "r") as f:
        for i in f.read().strip().splitlines():
            data.append(i.split(","))
    for d in data:
        if d[0] == username:
            return f'Username: {d[0]}<br>Full name: {d[2]}<br>Class: {d[4]}<br>Verified: {d[5]}'
    return f"User '{username}' not found"
        
#error handling
@app.route("/error")
def error():
    if request.args.get('error'):
        return request.args.get('error')
    resp = make_response(redirect("/"))
    return resp

#404 page not found error handling
@app.errorhandler(404)
def page_not_found(e):
    return "this page doesnt exist", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(debug=True, host="0.0.0.0", port=port)
