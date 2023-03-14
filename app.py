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

@app.route("/")
def home():
    return render_template("index.html")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "Savingtheworld1 Account Verification"
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

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
                data.append(i.split(","))
        for d in data:
            if username == d[0] and password == d[1]:
                cookie = str(uuid.uuid4())
                with open("db/sessions", "a") as f:
                    f.write("\n" + username + " " + cookie)
                resp = make_response(redirect("/users/" + username))
                resp.set_cookie("user", cookie)
                return resp
        resp = make_response(redirect("/error?error=Incorrect username and/or password"))
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
        username = request.form["username"].strip().replace("\n", " ").replace(",", " ")
        email = request.form["email"].strip().replace("\n", " ").replace(",", " ")
        class_ = request.form["class"].strip().replace("\n", " ").replace(",", " ")
        fullname = request.form["fullname"].strip().replace("\n", " ").replace(",", " ")
        if not re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[-]?\w+[.]\w{2,3}$", email): #check if email is valid using regex
            resp = make_response(redirect("/error?error=Email is invalid"))
            return resp
        data = []
        with open("db/users", "r") as f:
            for i in f.read().splitlines():
                data.append(i.split(","))
        for d in data:
            print(d)
            if username == d[0]:
                resp = make_response(redirect("/error?error=Username is in use already"))
                return resp
            if email == d[3]:
                resp = make_response(redirect("/error?error=Email is in use already"))
                return resp
        password = ""
        for i in range(15):
            password += random.choice(alphanumeric)
        print(password)
        with open('db/users', 'a') as f:
            adding = '\n' + username + ',' + str(sha256(str(password + salt).encode("utf-8")).hexdigest()) + ',' + fullname + ',' + email + ',' + class_ + ',' + 'false'
            f.write(adding)
        send_email("Blog account activated", f"Login to your account with these details:\nusername:{username}\npassword:{password}", myemail, [email], mypassword)
        return "check your email bruhhhhh"
    else:
        return render_template("register.html")

@app.route("/error")
def error():
    #in case any error
    if request.args.get('error'):
        return request.args.get('error')
    return make_response(redirect("/"))

@app.errorhandler(404)
def page_not_found(e):
    return "this page doesnt exist", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(debug=True, host="0.0.0.0", port=port)
