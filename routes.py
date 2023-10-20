import secrets
from app import app
from flask import render_template, request, redirect, session, flash, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from datetime import datetime, timedelta

from db import db
from db_queries import (create_user, get_user, get_student_id, get_student_name, get_all_students, create_student, 
                        count_associations, delete_student, associated_courses, get_activity_data, get_course_name, 
                        get_course_id, get_course_students, create_course, delete_associations, create_associations,
                        remove_course, set_grades, get_students_data, update_activity, set_activity, 
                        get_all_courses, get_students_and_courses, search_students)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    ''' Create user 'gollum' for testing the application:
    test_user = "gollum"
    test_password = "#precious1"
    hash_value = generate_password_hash(test_password)
    result = get_user(test_user)
    if not result:
        create_user(test_user, hash_value)
    '''
    
    username = request.form["username"]
    password = request.form["password"]
    user = get_user(username)
    if not user:
        flash("Väärä käyttäjätunnus tai salasana", "error")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["user_id"] = user[0]
            session["csrf_token"] = secrets.token_hex(16)
        else:
            flash("Väärä käyttäjätunnus tai salasana", "error")
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        existing_user = get_user(username)
        if existing_user:
            flash(f"Käyttäjä {username} on jo olemassa.", "error")
        elif password1 != password2:
            flash("Annetut salasanat eivät täsmää.", "error")
        else:
            hash_value = generate_password_hash(password1)
            create_user(username, hash_value)
            flash(f"Käyttäjän {username} lisääminen onnistui.", "success")
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/students", methods=["GET", "POST"])
def students():
    creator_id = session.get("user_id")
    search_query = request.form.get("search_query", "")
    action = request.form.get("action")
    students = []
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token")
        csrf_token = session.get("csrf_token")
        if submitted_token == csrf_token:
            if action == "search":
                students = search_students(creator_id, search_query)
            elif action == "add_student":
                student_name = request.form["student_name"]
                existing_student = get_student_id(student_name, creator_id)
                if existing_student:
                    flash("Tällä nimellä on jo oppilas. Käytä yksilöllistä nimeä.", "error")
                else:
                    try:
                        create_student(student_name, creator_id)
                        flash(f"{student_name} lisättiin onnistuneesti.", "success")
                    except Exception:
                        db.session.rollback()
                        flash("Uuden oppilaan lisääminen epäonnistui.", "error")
        else:
            flash("Virheellinen CSRF-token", "error")
            return "Invalid CSRF token", 403
    if not students:
        students = get_all_students(creator_id)
    return render_template("students.html", students=students)

@app.route("/student/<int:student_id>", methods=["GET", "POST"])
def student(student_id):
    creator_id = session.get("user_id")
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token")
        csrf_token = session.get("csrf_token")
        if submitted_token == csrf_token:
            course_count = count_associations(student_id)
            # Student is associated with courses:
            if course_count > 0:
                flash("Oppilas osallistuu jollekin kurssille, jolloin poisto on kielletty.", "error")
            # Delete student from the database based on their ID
            else:
                delete_student(student_id)
                return redirect("/students")
        else:
            flash("Virheellinen CSRF-token", "error")
            return "Invalid CSRF token", 403
    error_messages = get_flashed_messages(category_filter=["error"])
    student_name = get_student_name(student_id, creator_id)
    course_names = associated_courses(student_id)

    # Fetch activity data for each course
    course_activities = {}
    for course in course_names:
        activity_data = get_activity_data(course.id, student_id)
        
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
    creator_id = session.get("user_id")
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token")
        csrf_token = session.get("csrf_token")
        if submitted_token == csrf_token:
            course_name = request.form["course_name"]
            existing_course = get_course_id(course_name, creator_id)
            if existing_course:
                flash("Tällä nimellä on jo kurssi. Käytä yksilöllistä nimeä.", "error")
            else:
                try:
                    create_course(course_name, creator_id)
                    flash(f"{course_name} lisättiin onnistuneesti.", "success")
                except Exception:
                    db.session.rollback()
                    flash("Uuden kurssin lisääminen epäonnistui", "error")
        else:
            flash("Virheellinen CSRF-token", "error")
            return "Invalid CSRF token", 403
    #courses = db.session.execute(text("SELECT * FROM courses")).fetchall()
    courses = get_all_courses(creator_id)
    return render_template("courses.html", courses=courses)

@app.route("/course_students/<int:course_id>")
def course_students(course_id):
    creator_id = session.get("user_id")
    course_name = get_course_name(course_id, creator_id)
    course_students = get_course_students(course_id, creator_id)
    students = get_all_students(creator_id)
    return render_template("course_students.html", students=students, course_name=course_name, course_id=course_id, course_students=course_students)

@app.route("/save_course_students/<int:course_id>", methods=["POST"])
def save_course_students(course_id):
    submitted_token = request.form.get("csrf_token")
    csrf_token = session.get("csrf_token")
    if submitted_token == csrf_token:
        creator_id = session.get("user_id")
        selected_student_ids = request.form.getlist("student_ids[]")
        # Fetch previous students:
        previous_course_students = get_course_students(course_id, creator_id)
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
                    delete_associations(course_id, student_ids_to_delete)
                    flash("Kurssilta poistettiin oppilas/oppilaita", "success")
            else:
                # Display confirmation dialog
                return render_template("confirmation.html", course_id=course_id, student_ids_to_delete=student_ids_to_delete_str)
        # Insert associations for the selected students and the course
        if selected_student_ids:
            for student_id in selected_student_ids:
                if student_id not in [str(student.id) for student in previous_course_students]:
                    create_associations(course_id, student_id)
            flash("Kurssille lisättiin oppilaita", "success")
        return redirect("/courses")
    else:
        return "Invalid CSRF token", 403

@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    submitted_token = request.form.get("csrf_token")
    csrf_token = session.get("csrf_token")
    if submitted_token == csrf_token:
        remove_course(course_id)
        flash("Kurssi poistettiin onnistuneesti", "success")
        return redirect("/courses")
    else:
        return "Invalid CSRF token", 403

@app.route("/grades", methods=["GET", "POST"])
def grades():
    creator_id = session.get("user_id")
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token")
        csrf_token = session.get("csrf_token")
        if submitted_token == csrf_token:
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
                        if grade:
                            set_grades(course_id, student_id, grade)
                        else:
                            set_grades(course_id, student_id, 0)
            flash("Arvosanat tallennettiin onnistuneesti.", "success")
            return redirect("/grades")
        else:
            flash("Virheellinen CSRF-token", "error")
            return "Invalid CSRF token", 403
    
    # Fetch students and their grades and courses
    students_data = get_students_data(creator_id)
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

        activity_data = get_activity_data(student_data.course_id, student_data.student_id)
        
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
    # For debugging:
    '''
    today = datetime.now()
    new_date = today + timedelta(days=1)
    current_date = new_date.strftime("%Y-%m-%d")
    '''
    creator_id = session.get("user_id")
    current_date = datetime.now().strftime("%Y-%m-%d")
    html_date = datetime.now().strftime("%d.%m.%Y")
    if request.method == "POST":
        submitted_token = request.form.get("csrf_token")
        csrf_token = session.get("csrf_token")
        if submitted_token == csrf_token:
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
                        #print("Day: ", day)
                        if current_date == day or day == '1900-01-01':
                            update_activity(course_id, student_id, score, current_date)
                            # print("UPDATE")
                        else:
                            set_activity(course_id, student_id, score, current_date)
                            # print("INSERT")
            flash("Tuntiaktiivisuusarvosanat tallennettiin onnistuneesti.", "success")
            return redirect("/activity")
        else:
            flash("Virheellinen CSRF-token", "error")
            return "Invalid CSRF token", 403
    # Fetch students and courses
    students_courses = get_students_and_courses(creator_id, current_date)
    courses = set(item.course_name for item in students_courses)

    return render_template("activity.html", students_courses=students_courses, courses=courses, current_date=html_date)
