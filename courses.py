from db import db
from sqlalchemy.sql import text

def associated_courses(student_id):
    sql = """
        SELECT courses.id, courses.name, course_students.grade
        FROM courses
        INNER JOIN course_students ON courses.id = course_students.course_id
        WHERE course_students.student_id = :student_id
    """
    return db.session.execute(text(sql), {"student_id": student_id}).fetchall()

def get_course_name(course_id, creator_id):
    sql = "SELECT name FROM courses WHERE id = :course_id AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"course_id": course_id, "creator_id": creator_id}).fetchone()[0]

def get_course_id(course_name, creator_id):
    sql = "SELECT id FROM courses WHERE name = :name AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"name": course_name, "creator_id": creator_id}).fetchone()

def get_all_courses(creator_id):
    sql = "SELECT id, name FROM courses WHERE creator_id = :creator_id ORDER BY name"
    return db.session.execute(text(sql), {"creator_id": creator_id}).fetchall()

def create_course(course_name, creator_id):
    sql = "INSERT INTO courses (name, creator_id) VALUES (:name, :creator_id)"
    db.session.execute(text(sql), {"name": course_name, "creator_id": creator_id})
    db.session.commit()

def remove_course(course_id):
    sql_delete_associations = "DELETE FROM course_students WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_associations), {"course_id": course_id})
    sql_delete_activities = "DELETE FROM activity WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_activities), {"course_id": course_id})
    sql_delete_course = "DELETE FROM courses WHERE id = :course_id"
    db.session.execute(text(sql_delete_course), {"course_id": course_id})
    db.session.commit()