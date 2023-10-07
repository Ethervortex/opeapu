import os
from app import app
from flask import render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from db import db
from db_queries import create_user, get_user, get_student_id, get_student_name, get_all_students, create_student, count_associations, delete_student, associated_courses, get_activity_data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    # Create user 'gollum' for testing the application:
    test_user = "gollum"
    test_password = "#precious1"
    hash_value = generate_password_hash(test_password)
    result = get_user(test_user)
    if not result:
        create_user(test_user, hash_value)
    
    username = request.form["username"]
    password = request.form["password"]
    user = get_user(username)
    if not user:
        flash("Väärä käyttäjätunnus tai salasana", "error")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["csrf_token"] = os.urandom(16).hex()
        else:
            flash("Väärä käyttäjätunnus tai salasana", "error")
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        student_name = request.form["student_name"]
        existing_student = get_student_id(student_name)
        if existing_student:
            flash("Tällä nimellä on jo tallennettuna oppilas. Käytä yksilöllistä nimeä.", "error")
        else:
            try:
                create_student(student_name)
                flash(f"{student_name} lisättiin tietokantaan onnistuneesti.", "success")
            except Exception:
                db.session.rollback()
                flash("Uuden oppilaan lisääminen epäonnistui.", "error")
    students = get_all_students()
    return render_template("students.html", students=students)

@app.route("/student/<int:student_id>", methods=["GET", "POST"])
def student(student_id):
    if request.method == "POST":
        course_count = count_associations(student_id)
        # Student is associated with courses:
        if course_count > 0:
            flash("Oppilas osallistuu jollekin kurssille, jolloin poisto on kielletty.", "error")
        # Delete student from the database based on their ID
        else:
            delete_student(student_id)
            return redirect("/students")
    error_messages = get_flashed_messages(category_filter=["error"])
    student_name = get_student_name(student_id)
    course_names = associated_courses(student_id)

    # Fetch activity data for each course
    course_activities = {}
    for course in course_names:
        activity_data = get_activity_data(course, student_id)
        
        total_score = 0
        absence = 0  # Count of -1 scores
        for activity in activity_data:
            if activity.activity_score is None:
                break
            if activity.activity_score != -1:
                total_score += activity.activity_score
            else:
                absence += 1

        mean_score = None
        if len(activity_data) - absence > 0:
            mean_score = total_score / (len(activity_data) - absence)
            mean_score = round(mean_score, 1)

        if course.grade is None:
            grade = "puuttuu"
        else:
            grade = course.grade

        # Store course activities in the dictionary
        course_activities[course.name] = {
            "activities": activity_data,
            "mean_score": mean_score,
            "absence": absence,
            "grade": grade
        }

    return render_template("student.html", student_id=student_id, student_name=student_name, error_messages=error_messages,
         course_names=course_names, course_activities=course_activities)

@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        course_name = request.form["course_name"]
        sql_existing = "SELECT id FROM courses WHERE name = :name"
        existing_course = db.session.execute(text(sql_existing), {"name": course_name}).fetchone()
        if existing_course:
            flash("Tämä kurssi on jo luotu. Käytä yksilöllistä nimeä.", "error")
        else:
            sql_insert_course = "INSERT INTO courses (name) VALUES (:name)"
            try:
                db.session.execute(text(sql_insert_course), {"name": course_name})
                db.session.commit()
                flash(f"{course_name} lisättiin tietokantaan onnistuneesti.", "success")
            except Exception:
                db.session.rollback()
                flash("Uuden kurssin lisääminen epäonnistui", "error")
    courses = db.session.execute(text("SELECT * FROM courses")).fetchall()
    return render_template("courses.html", courses=courses)

@app.route("/course_students/<int:course_id>")
def course_students(course_id):
    sql_course_name = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(text(sql_course_name), {"course_id": course_id}).fetchone()[0]
    sql_course_students = """
        SELECT students.id, students.name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        WHERE course_students.course_id = :course_id
    """
    course_students = db.session.execute(text(sql_course_students), {"course_id": course_id}).fetchall()
    sql_all = "SELECT id, name FROM students"
    students = db.session.execute(text(sql_all)).fetchall()
    return render_template("course_students.html", students=students, course_name=course_name, course_id=course_id, course_students=course_students)

@app.route("/save_course_students/<int:course_id>", methods=["POST"])
def save_course_students(course_id):
    selected_student_ids = request.form.getlist("student_ids[]")
    # Fetch previous students:
    sql_course_students = '''
        SELECT students.id, students.name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        WHERE course_students.course_id = :course_id
    '''
    previous_course_students = db.session.execute(text(sql_course_students), {"course_id": course_id}).fetchall()
    student_ids_to_delete = [student.id for student in previous_course_students if str(student.id) not in selected_student_ids]
    student_ids_to_delete_str = ",".join(map(str, student_ids_to_delete))
    # Delete students from the course_students and activity tables
    if student_ids_to_delete:
        # JavaScript confirmation dialog
        confirmation = request.form.get("confirmation")
        conf = request.form.get("conf")
        if confirmation == "true" or conf == "true":
            student_ids_to_delete_str = request.form.get("student_ids_to_delete")
            students_to_delete = student_ids_to_delete_str.split(',')
            student_ids_to_delete = [int(id) for id in students_to_delete]
            # Delete students from the course_students and activity tables
            if students_to_delete:
                sql_delete_course_students = '''
                    DELETE FROM course_students
                    WHERE course_id = :course_id
                    AND student_id = ANY(:student_ids_to_delete)
                '''
                db.session.execute(text(sql_delete_course_students), {"course_id": course_id, "student_ids_to_delete": student_ids_to_delete})

                sql_delete_activity = '''
                    DELETE FROM activity
                    WHERE course_id = :course_id
                    AND student_id = ANY(:student_ids_to_delete)
                '''
                db.session.execute(text(sql_delete_activity), {"course_id": course_id, "student_ids_to_delete": student_ids_to_delete})
        else:
            # Display confirmation dialog
            return render_template("confirmation.html", course_id=course_id, student_ids_to_delete=student_ids_to_delete_str)
     # Insert associations for the selected students and the course
    if selected_student_ids:
        # Table: course_students
        sql_insert1 = "INSERT INTO course_students (course_id, student_id) VALUES (:course_id, :student_id)"
        # Table: activity
        sql_insert2 = "INSERT INTO activity (course_id, student_id, activity_date) VALUES (:course_id, :student_id, '1900-01-01')"
        for student_id in selected_student_ids:
            if student_id not in [str(student.id) for student in previous_course_students]:
                db.session.execute(text(sql_insert1), {"course_id": course_id, "student_id": student_id})
                db.session.execute(text(sql_insert2), {"course_id": course_id, "student_id": student_id})
    db.session.commit()
    return redirect("/courses") 

@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    sql_delete_associations = "DELETE FROM course_students WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_associations), {"course_id": course_id})

    sql_delete_activities = "DELETE FROM activity WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_activities), {"course_id": course_id})

    sql_delete_course = "DELETE FROM courses WHERE id = :course_id"
    db.session.execute(text(sql_delete_course), {"course_id": course_id})

    db.session.commit()
    return redirect("/courses")

@app.route("/grades", methods=["GET", "POST"])
def grades():
    if request.method == "POST":
        selected_course = request.form.get("course")
        # print("Selected course:", selected_course) # debug
        # Iterate through the form data to retrieve and update grades
        for student_input_name, grade in request.form.items():
            if student_input_name.startswith("grade-"):
                # print("student_input_name:", student_input_name) # debug
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
    students_data = db.session.execute(text(sql)).fetchall()
    courses = set(item.course_name for item in students_data)

    # Fetch activity data for each course
    students_courses = {}
    for student_data in students_data:
        course_name = student_data.course_name

        # Initialize an empty list for students in this course if it doesn't exist
        if course_name not in students_courses:
            students_courses[course_name] = {
                "students": []
            }

        sql_activity_data = """
            SELECT activity_date, activity_score
            FROM activity
            WHERE course_id = :course_id AND student_id = :student_id
        """
        activity_data = db.session.execute(text(sql_activity_data), {
            "course_id": student_data.course_id,
            "student_id": student_data.student_id
        }).fetchall()
        
        total_score = 0
        absence = 0  # Count of -1 scores
        for activity in activity_data:
            if activity.activity_score is None:
                break
            if activity.activity_score != -1:
                total_score += activity.activity_score
            else:
                absence += 1
        mean_score = None
        if len(activity_data) - absence > 0:
            mean_score = total_score / (len(activity_data) - absence)
            mean_score = round(mean_score, 1)

        students_courses[course_name]["students"].append({
            "student_id": student_data.student_id,
            "student_name": student_data.student_name,
            "course_id": student_data.course_id,
            "grade": student_data.grade,
            "mean_score": mean_score,
            "absence": absence
        })
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
                            "activity_score": score if score != '' else -1, 
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
                                "activity_score": score if score != '' else -1,
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

    return render_template("activity.html", students_courses=students_courses, courses=courses, current_date=html_date)
