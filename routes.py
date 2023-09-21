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
    #Create user 'testiope' for testing the application:
    test_user = "testiope"
    test_password = "salasana"
    sql = "SELECT * FROM users WHERE username = :username"
    result = db.session.execute(text(sql), {"username": test_user}).fetchone()
    print("Testiope:", result) # debug
    if not result:
        create_user(test_user, test_password)
    
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT id, password FROM users WHERE username = :username"
    user = db.session.execute(text(sql), {"username": username}).fetchone()
    if not user:
        print("Käyttäjää ei löydy.") # debug
        #return render_template("error.html", message="Virhe: Väärä käyttäjätunnus")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            #session["csrf_token"] = secrets.token_hex(16)
        else:
            print("Väärä salasana") # debug
            #return render_template("error.html", message="Virhe: Väärä salasana")
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        student_name = request.form["student_name"]
        sql = "INSERT INTO students (name) VALUES (:name)"
        try:
            db.session.execute(text(sql), {"name": student_name})
            db.session.commit()
            print(student_name, " lisätty tietokantaan") # debug
        except:
            db.session.rollback()
            print("Uuden oppilaan lisääminen epäonnistui") # debug
    sql = "SELECT * FROM students"
    students = db.session.execute(text(sql)).fetchall()
    return render_template("students.html", students=students)

@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        course_name = request.form["course_name"]
        sql = "INSERT INTO courses (name) VALUES (:name)"
        try:
            db.session.execute(text(sql), {"name": course_name})
            db.session.commit()
            print(course_name, " lisätty tietokantaan") # debug
        except:
            db.session.rollback()
            print("Uuden kurssin lisääminen epäonnistui") # debug
    courses = db.session.execute(text("SELECT * FROM courses")).fetchall()
    return render_template("courses.html", courses=courses)

@app.route("/course_students/<int:course_id>")
def course_students(course_id):
    sql_course_name = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(sql_course_name), {"course_id": course_id}).fetchone()[0]
    sql = "SELECT * FROM students"
    students = db.session.execute(text(sql)).fetchall()
    return render_template("course_students.html", students=students, course_name=course_name, course_id=course_id)

@app.route("/save_course_students/<int:course_id>", methods=["POST"])
def save_course_students(course_id):
    if request.method == "POST":
        selected_student_ids = request.form.getlist("student_ids[]")
        print("course_id", course_id)

        sql_delete = "DELETE FROM course_students WHERE course_id = :course_id"
        db.session.execute(text(sql_delete), {"course_id": course_id})

        # Insert associations for the selected students and the course
        if selected_student_ids:
            sql_insert = "INSERT INTO course_students (course_id, student_id) VALUES (:course_id, :student_id)"
            for student_id in selected_student_ids:
                db.session.execute(text(sql_insert), {"course_id": course_id, "student_id": student_id})

        db.session.commit()
        return redirect("/courses") 

    return "Invalid Request"

@app.route("/grades")
def grades():
    # Fetch courses from the database
    sql = "SELECT * FROM courses"
    courses = db.session.execute(text(sql)).fetchall()

    return render_template("grades.html", courses=courses)