from app import app
from flask import render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from datetime import datetime, timedelta

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
    #print("Testiope:", result) # debug
    if not result:
        create_user(test_user, test_password)
    
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT id, password FROM users WHERE username = :username"
    user = db.session.execute(text(sql), {"username": username}).fetchone()
    #error_messages = get_flashed_messages(category_filter=["error"])
    if not user:
        #print("Käyttäjää ei löydy.") # debug
        flash("Väärä käyttäjätunnus", "error")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            #session["csrf_token"] = secrets.token_hex(16)
            #os.urandom(16).hex()
        else:
            #print("Väärä salasana") # debug
            flash("Väärä salasana", "error")
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

@app.route("/student/<int:student_id>", methods=["GET", "POST"])
def student(student_id):
    if request.method == "POST":
        sql_check_courses = "SELECT COUNT(*) FROM course_students WHERE student_id = :student_id"
        course_count = db.session.execute(text(sql_check_courses), {"student_id": student_id}).fetchone()[0]
        # Student is associated with courses:
        if course_count > 0:
            flash("Oppilas osallistuu jollekin kurssille, jolloin poisto on kielletty.", "error")
        # Delete student from the database based on their ID
        else:
            sql_delete_student = "DELETE FROM students WHERE id = :student_id"
            db.session.execute(text(sql_delete_student), {"student_id": student_id})
            db.session.commit()
            return redirect("/students")
    error_messages = get_flashed_messages(category_filter=["error"])
    sql_student_name = "SELECT name FROM students WHERE id = :student_id"
    student_name = db.session.execute(text(sql_student_name), {"student_id": student_id}).fetchone()[0]
    return render_template("student.html", student_id=student_id, student_name=student_name, error_messages=error_messages)


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
        # print("course_id", course_id) # debug

        sql_delete = "DELETE FROM course_students WHERE course_id = :course_id"
        db.session.execute(text(sql_delete), {"course_id": course_id})

        # Insert associations for the selected students and the course
        if selected_student_ids:
            # Table: course_students
            sql_insert1 = "INSERT INTO course_students (course_id, student_id) VALUES (:course_id, :student_id)"
            # Table: activity
            sql_insert2 = "INSERT INTO activity (course_id, student_id, activity_date) VALUES (:course_id, :student_id, '1900-01-01')"
            for student_id in selected_student_ids:
                db.session.execute(text(sql_insert1), {"course_id": course_id, "student_id": student_id})
                db.session.execute(text(sql_insert2), {"course_id": course_id, "student_id": student_id})


        db.session.commit()
        return redirect("/courses") 

    return "Invalid Request"

@app.route("/grades", methods=["GET", "POST"])
def grades():
    if request.method == "POST":
        selected_course = request.form.get("course")

        # Iterate through the form data to retrieve and update grades
        for student_input_name, grade in request.form.items():
            if student_input_name.startswith("grade-"):
                parts = student_input_name.split("-")
                student_id = parts[1]
                course_id = parts[2]
                student_course = request.form.get("student_course-{}-{}".format(student_id, course_id))
                # print(selected_course, student_course) # debug
                if student_course == selected_course:
                    sql_update = """
                        UPDATE course_students
                        SET grade = :grade
                        WHERE course_id = :course_id AND student_id = :student_id
                    """
                    db.session.execute(text(sql_update), {"course_id": int(course_id), "student_id": int(student_id), "grade": grade})
                    db.session.commit()
                    # print("Student:", student_id, student_input_name, "course_id", course_id, "Grade:", grade)  # debug
        flash("Arvosanat tallennettiin onnistuneesti!", "success")
        return redirect("/grades")
    
    # Fetch students and their grades and courses
    sql = """
        SELECT students.id AS student_id, students.name AS student_name, course_students.grade, courses.id AS course_id, courses.name AS course_name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        LEFT JOIN courses ON course_students.course_id = courses.id
        ORDER BY courses.id, students.id
    """
    students_courses = db.session.execute(text(sql)).fetchall()
    courses = set(item.course_name for item in students_courses)

    return render_template("grades.html", students_courses=students_courses, courses=courses)

@app.route("/activity", methods=["GET", "POST"])
def activity():
    ''' For debugging:
    today = datetime.now()
    new_date = today + timedelta(days=4)
    current_date = new_date.strftime("%Y-%m-%d")
    '''

    current_date = datetime.now().strftime("%Y-%m-%d")
    html_date = datetime.now().strftime("%d.%m.%Y")
    if request.method == "POST":
        selected_course = request.form.get("course")

        # Iterate through the form data to retrieve and update scores
        for student_input_name, score in request.form.items():
            if student_input_name.startswith("grade_"):
                parts = student_input_name.split("_")
                student_id = parts[1]
                course_id = parts[2]
                day = parts[3]
                student_course = request.form.get("student_course-{}-{}".format(student_id, course_id))
                # print(selected_course, student_course) # debug
                if student_course == selected_course:
                    print("Day: ", day)
                    if current_date == day or day == '1900-01-01':
                        sql_update = """
                            UPDATE activity
                            SET
                                activity_date = CASE
                                    WHEN activity_date = '1900-01-01' THEN :activity_date
                                    ELSE activity_date
                                END,
                                activity_score = :activity_score
                            WHERE course_id = :course_id AND student_id = :student_id
                                AND (activity_date = :activity_date OR activity_date = '1900-01-01')
                        """
                        db.session.execute(text(sql_update), {
                            "course_id": int(course_id), 
                            "student_id": int(student_id), 
                            "activity_score": score, 
                            "activity_date": current_date,
                            },
                        )
                        print("UPDATE")
                        # print("Student:", student_id, student_input_name, "course_id", course_id, "Score:", score)  # debug
                    else:
                        sql_insert = """
                            INSERT INTO activity (course_id, student_id, activity_score, activity_date)
                            VALUES (:course_id, :student_id, :activity_score, :activity_date)
                        """
                        db.session.execute(text(sql_insert), {
                                "course_id": int(course_id),
                                "student_id": int(student_id),
                                "activity_score": score,
                                "activity_date": current_date,
                            },
                        )
                        print("INSERT")
                    db.session.commit()
        flash("Tuntiaktiivisuusarvosanat tallennettiin onnistuneesti!", "success")
        return redirect("/activity")
    # Fetch students and courses
    sql_names = """
        SELECT students.id AS student_id, students.name AS student_name, MAX(activity.activity_date) AS day,
            activity.course_id AS course_id, courses.name AS course_name
        FROM students
        INNER JOIN activity ON students.id = activity.student_id
        LEFT JOIN courses ON activity.course_id = courses.id
        GROUP BY students.id, students.name, activity.course_id, courses.name
    """
    
    students_courses = db.session.execute(text(sql_names)).fetchall()
    courses = set(item.course_name for item in students_courses)
    #names = set(item.student_name for item in students_courses)
    return render_template("activity.html", students_courses=students_courses, courses=courses, current_date=html_date)
