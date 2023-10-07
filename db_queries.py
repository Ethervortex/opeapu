from db import db
from sqlalchemy.sql import text

def create_user(username, hash_value):
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(text(sql), {"username":username, "password":hash_value})
    db.session.commit()
    return "User created"

def get_user(username):
    sql = "SELECT id, password FROM users WHERE username = :username"
    return db.session.execute(text(sql), {"username": username}).fetchone()

def get_student_id(student_name):
    sql = "SELECT id FROM students WHERE name = :name"
    return db.session.execute(text(sql), {"name": student_name}).fetchone()

def get_student_name(student_id):
    sql = "SELECT name FROM students WHERE id = :student_id"
    return db.session.execute(text(sql), {"student_id": student_id}).fetchone()[0]

def get_all_students():
    sql = "SELECT id, name FROM students"
    return db.session.execute(text(sql)).fetchall()

def create_student(student_name):
    sql = "INSERT INTO students (name) VALUES (:name)"
    db.session.execute(text(sql), {"name": student_name})
    db.session.commit()

def delete_student(student_id):
    sql = "DELETE FROM students WHERE id = :student_id"
    db.session.execute(text(sql), {"student_id": student_id})
    db.session.commit()

def count_associations(student_id):
    sql = "SELECT COUNT(*) FROM course_students WHERE student_id = :student_id"
    return db.session.execute(text(sql), {"student_id": student_id}).fetchone()[0]

def associated_courses(student_id):
    sql = """
        SELECT courses.id, courses.name, course_students.grade
        FROM courses
        INNER JOIN course_students ON courses.id = course_students.course_id
        WHERE course_students.student_id = :student_id
    """
    return db.session.execute(text(sql), {"student_id": student_id}).fetchall()

def get_activity_data(course, student_id):
    sql = """
            SELECT activity_date, activity_score
            FROM activity
            WHERE course_id = :course_id AND student_id = :student_id
        """
    return db.session.execute(text(sql), {"course_id": course.id, "student_id": student_id}).fetchall()