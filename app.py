from flask import Flask, make_response, render_template, redirect, request
from hashlib import sha256
import os
import uuid
from secret import myemail, mypassword, salt
import smtplib
from email.mime.text import MIMEText
import re
import string
import markdown
from werkzeug.utils import secure_filename
from markupsafe import escape

alphanumeric = string.ascii_letters + string.digits

app = Flask(__name__)
UPLOAD_FOLDER = 'db_images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# send emails to verify account


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "Savingtheworld1 Account Verification"
    msg["To"] = ", ".join(recipients)
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()


# check login
def checklogin():
    if request.cookies.get("user"):
        cookie = request.cookies.get("user")
        cookies = []
        with open("db/sessions", "r") as f:
            for i in f.read().strip().splitlines():
                data = i.split(",")
                cookies.append(data)
        for a in cookies:
            if cookie == a[1]:
                return True, a[0]
    return False, None


# home page, to update
@app.route("/")
def home():
    loggedin, username = checklogin()
    return render_template("index.html", loggedin=loggedin, username=username)

# login handler


@app.route("/login", methods=["POST", "GET"])
@app.route("/login/", methods=["POST", "GET"])
def login():
    # checks whether user is logged in arld
    loggedin, username = checklogin()
    if loggedin:
        return redirect("/users/" + username)
    # logs in if username and password is correct
    if request.method == "POST":
        username = request.form["username"].strip()
        password = str(
            sha256(
                str(request.form["password"].strip() + salt).encode("utf-8")
            ).hexdigest()
        )
        data = []
        with open("db/users", "r") as f:
            for i in f.read().strip().splitlines():
                data.append(i.split(","))
        for d in data:
            if username == d[0] and password == d[1]:
                cookie = str(uuid.uuid4())
                cookies = []
                with open("db/sessions", "r") as f:
                    a = f.read().strip().splitlines()
                    for b in a:
                        cookies.append(b.split(","))
                with open("db/sessions", "w") as f:
                    adding = ""
                    for c in cookies:
                        if c[0] != username:
                            adding += f"{c[0]},{c[1]}\n"
                    adding += f"{username},{cookie}\n"
                    f.write(adding)
                resp = make_response(redirect("/users/" + username))
                resp.set_cookie("user", cookie)
                return resp
        return make_response(
            redirect("/error?error=Incorrect username and/or password")
        )
    else:
        return render_template("login.html")


# register new account
@app.route("/register", methods=["POST", "GET"])
@app.route("/register/", methods=["POST", "GET"])
def register():
    # checks whether user is logged in arld
    loggedin, selfusername = checklogin()
    if loggedin:
        return redirect("/users/" + selfusername)
    # registers new user and sends confirmation email after validating their data
    if request.method == "POST":
        username = request.form["username"].strip().replace("\n", "")
        if not username.isalnum():
            return make_response(redirect("/error?error=Username contains invalid characters"))
        if len(username) < 4:
            return make_response(redirect("/error?error=Username is too short"))
        if len(username) > 20:
            return make_response(redirect("/error?error=Username is too long"))
        email = request.form["email"].strip().replace(
            "\n", "").replace(",", "")
        password = request.form["password"].strip().replace("\n", "")
        if not password.isalnum():
            return make_response(redirect("/error?error=Password contains invalid characters"))
        if len(password) < 12:
            return make_response(redirect("/error?error=Password is too short"))
        if len(password) > 20:
            return make_response(redirect("/error?error=Password is too long"))
        class_ = request.form["class"].strip().replace(
            "\n", "").replace(",", "")
        if not (class_ == "24/11" or class_ == "24/12" or class_ == "24/13" or class_ == "24/14" or class_ == "Teacher"):
            return make_response(redirect("/error?error=Class is invalid"))
        fullname = request.form["fullname"].strip().replace(
            "\n", "").replace(",", "")
        # check if email is valid using regex
        if not re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[-]?\w+[.]\w{2,3}$", email):
            return make_response(redirect("/error?error=Email is invalid"))
        data = []
        with open("db/users", "r") as f:
            for i in f.read().strip().splitlines():
                data.append(i.split(","))
        for d in data:
            if username == d[0]:
                return make_response(redirect("/error?error=Username is in use already"))
            if email == d[3]:
                return make_response(redirect("/error?error=Email is in use already"))
        with open("db/users", "a") as f:
            adding = (username + "," + str(sha256(str(password + salt).encode("utf-8")).hexdigest()
                                           ) + "," + fullname + "," + email + "," + class_ + "," + "False" + "\n")
            f.write(adding)
        with open(f'db/datauser/{username}', 'w') as f:
            f.write("")
        token = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())
        with open("db/verification", "a") as f:
            f.write(username + "," + token + "\n")
        send_email("Blog account activated",
                   f"Please verify your email before using your account {request.url_root}verify?token={token}", myemail, [email], mypassword)
        cookie = str(uuid.uuid4())
        with open("db/sessions", "a") as f:
            f.write(username + "," + cookie + "\n")
        resp = make_response(redirect("/verify"))
        resp.set_cookie("user", cookie)
        return resp
    else:
        return render_template("register.html")


# verify email
@app.route("/verify")
@app.route("/verify/")
def verify():
    loggedin, username = checklogin()
    if request.args.get("token"):
        token = request.args.get("token")
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
                        f.write(
                            f"{user[0]},{user[1]},{user[2]},{user[3]},{user[4]},{user[5]}\n"
                        )
                with open("db/verification", "w") as f:
                    for d in data:
                        if d[1] != token:
                            f.write(f"{d[0]},{d[1]}\n")
                return render_template("verified.html", loggedin=loggedin, username=username)
        return make_response(redirect("/error?error=Verification link is either invalid or has expired"))
    return render_template("verify.html", loggedin=loggedin, username=username)


# displays current users, fullname, verified status
@app.route("/users")
@app.route("/users/")
def user():
    loggedin, username = checklogin()
    data = []
    with open("db/users", "r") as f:
        for i in f.read().strip().splitlines():
            data.append(i.split(","))
    return render_template("users.html", length=len(data), users=data, loggedin=loggedin, username=username)


# logout page for user
@app.route("/logout")
def logout():
    if request.cookies.get("user"):
        resp = make_response(redirect("/logout"))
        resp.set_cookie("user", "", expires=0)
        return resp
    return render_template("logout.html")


# user page which show
@app.route("/users/<username>")
@app.route("/users/<username>/")
def userpage(username):
    loggedin, selfusername = checklogin()
    data = []
    with open("db/users", "r") as f:
        for i in f.read().strip().splitlines():
            data.append(i.split(","))
    for d in data:
        if d[0] == username:
            postdata = []
            with open(f"db/datauser/{username}", 'r') as f:
                for postid in f:
                    with open(f"db/datapost/{postid}") as k:
                        k = k.read().splitlines()
                        a = k[0].split(",")
                        postdata.append([a[1],a[2],a[4],a[5],k[1]])
            return render_template("user.html", loggedin=loggedin, data=d, username=selfusername, postdata=postdata)
    return render_template("error.html", text=f'User {username} does not exist.')


# create a post page
@app.route("/post", methods=["POST", "GET"])
@app.route("/post/", methods=["POST", "GET"])
def post():
    loggedin, username = checklogin()
    data = []
    with open("db/users", "r") as f:
        for i in f.read().strip().splitlines():
            data.append(i.split(","))
    for d in data:
        if d[0] == username:
            if d[5] == "False":
                return make_response(redirect("/error?error=You are not a verified user. Verify your email first before posting any kind of content."))
    if request.method == "POST" and username:
        filename = 'noimage'
        title = request.form["title"].strip().replace("\n", "")
        if not all(x.isalnum() or x.isspace() for x in title):
            return make_response(redirect("/error?error=Title contains invalid characters"))
        if len(title) < 5:
            return make_response(redirect("/error?error=Title is too short"))
        if len(title) > 50:
            return make_response(redirect("/error?error=Title is too long"))
        description = request.form["description"].strip().replace("\n", "")
        if len(description) < 20:
            return make_response(redirect("/error?error=Description is too short"))
        if len(description) > 150:
            return make_response(redirect("/error?error=Description is too long"))
        post_ = escape(request.form["post"].strip())
        authorname = request.form["authorname"].strip().replace("\n", "")
        if not all(x.isalnum() or x.isspace() or x == "-" for x in authorname):
            return make_response(redirect("/error?error=Title contains invalid characters"))
        if len(authorname) < 5:
            return make_response(redirect("/error?error=Author's name is too short"))
        if len(authorname) > 25:
            return make_response(redirect("/error?error=Author's name is too long"))
        postid = str(uuid.uuid4())
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = str(uuid.uuid4()) + '_' + \
                        secure_filename(file.filename).replace(",", "")
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))
                else:
                    return make_response(redirect("/error?error=File type is invalid, accepts only .png, .jpg and .jpeg"))
        with open(f'db/datapost/{postid}', "w+") as f:
            adding = f'{username},{title},{authorname},{filename},0,0\n{description}\n{post_}'
            f.write(adding)
        with open(f'db/datauser/{username}', 'a') as f:
            adding = f'{postid}\n'
        return make_response(redirect(f"/users/{username}"))
    elif username:
        return render_template("post.html", loggedin=loggedin, username=username)
    else:
        return make_response(redirect("/login"))


# error handling
@app.route("/error")
@app.route("/error/")
def error():
    loggedin, username = checklogin()
    if request.args.get("error"):
        return render_template("error.html", text=request.args.get("error"), loggedin=loggedin, username=username)
    resp = make_response(redirect("/"))
    return resp


# 404 page not found error handling
@app.errorhandler(404)
def page_not_found(e):
    return make_response(
        redirect("/error?error=Page does not exist")
    ), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(debug=True, host="0.0.0.0", port=port)
