from app import app
from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text

from db import db

def create_user(username, password):
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(text(sql), {"username":username, "password":hash_value})
    db.session.commit()
    return "User created"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    '''
    test_user = "testiope"
    test_password = "salasana"
    result = db.session.execute(text("SELECT * FROM users WHERE username = :username"), {"username": test_user}).fetchone()
    print("Testiope:", result)
    if not result:
        create_user(test_user, test_password)
    '''
    username = request.form["username"]
    password = request.form["password"]
    user = db.session.execute(text("SELECT id, password FROM users WHERE username = :username"), {"username": username}).fetchone()
    if not user:
        print("Käyttäjää ei löydy.") # debug
        #return render_template("error.html", message="Virhe: Väärä käyttäjätunnus")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
        else:
            print("Väärä salasana") # debug
            #return render_template("error.html", message="Virhe: Väärä salasana")
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")