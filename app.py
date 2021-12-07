from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from random import randint
from flask_mail import *


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mail = Mail(app)
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'studybuddycs50@gmail.com'  
app.config['MAIL_PASSWORD'] = 'Study2///'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
mail = Mail(app)  
code = randint(000000,999999)

db = SQL("sqlite:///cs50.db")

#make helper function instead
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
    

@app.route("/")
@login_required
def index():
    user_id = session["id"]
    results = db.execute(f"SELECT * FROM users JOIN matches ON matches.match_id = users.id WHERE matches.id = {user_id}")
    return render_template("index.html", results=results)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return render_template("error.html", message="Username is empty!"), 403
        elif not password:
            return render_template("error.html", message="Password is empty!"), 403
        result = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
        if len(result) == 0: 
            return render_template("error.html", message="Invalid username!"), 403
        elif not check_password_hash(result[0]["password"], password):
            return render_template("error.html", message="Password is incorrect!"), 403
        session["id"] = result[0]["id"]
        return redirect("/")
    return render_template("login.html")


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    if request.method == "POST":
        weights = [1.6, 0.8, 1.6, 1, 1, 0.8]
        criteria = ["college", "concentration", "class", "daychoice", "time", "place"]
        matches_count = {}
        user_id = session["id"]
        user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]
        college = request.form.get("college") or user["college"]
        concentration = request.form.get("concentration") or user["concentration"]
        class_of = request.form.get("class_of") or user["class"]
        daychoice = request.form.get("daychoice") or user["daychoice"]
        time = request.form.get("time") or user["time"]
        place = request.form.get("place") or user["place"]
        user_response = [college, concentration, class_of, daychoice, time, place]
        db.execute(f"UPDATE users SET college = '{college}', class = '{class_of}', concentration = '{concentration}', daychoice = '{daychoice}', time = '{time}', place = '{place}' WHERE id = {user_id}")
        for i in range(2):
            match = db.execute(f"SELECT id FROM users WHERE id != {user_id} AND {criteria[i]} LIKE '%{user_response[i]}%'")
            print(match)
            for j in range(len(match)):
                if match[j]["id"] not in matches_count:
                    matches_count[match[j]["id"]] = weights[i]
                else:
                    matches_count[match[j]["id"]] += weights[i]
        for i in range(2,6):
            match = db.execute(f"SELECT id FROM users WHERE id != {user_id} AND {criteria[i]} = '{user_response[i]}'")
            
            for j in range(len(match)):
                if match[j]["id"] not in matches_count:
                    matches_count[match[j]["id"]] = weights[i]
                else:
                    matches_count[match[j]["id"]] += weights[i]
        #should i put any variable definition above
        first_five = []
        print(matches_count)
        if len(matches_count):
            for match in sorted(matches_count, key=matches_count.get, reverse=True):
                print(match, matches_count[match])
                first_five.append(match)
            #check if there's a python ternary operator or python max operator
            length = len(first_five)
            if length > 5:
                length = 5
            db.execute(f"DELETE FROM matches WHERE id = {user_id}")
            for i in range(length):
                db.execute(f"INSERT INTO matches (id, match_id) VALUES ({user_id}, {first_five[i]})")
        return redirect("/")            
    return render_template("preferences.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        phone = request.form.get("phone")
        email = request.form.get("email")

        confirmation = request.form.get("confirmpassword")
        istaken = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
        if not username:
            return render_template("error.html", message="Username is empty!"), 400
        elif not firstname:
            return render_template("error.html", message="First name is empty!"), 400
        elif not lastname:
            return render_template("error.html", message="Last name is empty!"), 400
        elif not phone:
            return render_template("error.html", message="Phone is empty!"), 400
        elif not email:
            return render_template("error.html", message="Email is empty!"), 400
        elif len(istaken):
            return render_template("error.html", message="Username is taken!"), 400
        elif not password:
            return render_template("error.html", message="Password is empty!"), 400
        elif password != confirmation:
            return render_template("error.html", message="Passwords don't match!"), 400
        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute(f"INSERT INTO users (username, password, firstname, lastname, email, phone) VALUES ('{username}', '{password}', '{firstname}', '{lastname}', '{email}', '{phone}')")
        rows = db.execute(f"SELECT id FROM users WHERE username = '{username}'")
        session["id"] = rows[0]["id"]
        return redirect("/")
    return render_template("signup.html")



@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form.get("email")
        msg = Message('Code',sender = 'studybuddycs50@gmail.com', recipients = [email]) 
        msg.body = str(code)
        mail.send(msg)
        return render_template("validateemail.html")
    return render_template("verify.html") 


@app.route("/validate", methods=["GET", "POST"])
def validate():
    if request.method == "POST":
        user_code = request.form.get("code")  
        if code == int(user_code):
            return render_template("resetpassword.html")
        else:
            return render_template("error.html", message="The email is invalid!")
    return render_template("validateemail.html")


@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if request.method == "POST":
        user_id = session["id"]
        password = request.form.get("password")
        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)        
        db.execute(f"UPDATE users SET password = '{password}' WHERE id = {user_id}")
    return render_template("resetpassword.html")