from db import db
from sqlalchemy.sql import text

def get_student_id(student_name, creator_id):
    sql = "SELECT id FROM students WHERE name = :name AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"name": student_name, "creator_id": creator_id}).fetchone()

def get_student_name(student_id, creator_id):
    sql = "SELECT name FROM students WHERE id = :student_id AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"student_id": student_id, "creator_id": creator_id}).fetchone()[0]

def get_all_students(creator_id):
    sql = "SELECT id, name FROM students WHERE creator_id = :creator_id ORDER BY name"
    return db.session.execute(text(sql), {"creator_id": creator_id}).fetchall()

def create_student(student_name, creator_id):
    sql = "INSERT INTO students (name, creator_id) VALUES (:name, :creator_id)"
    db.session.execute(text(sql), {"name": student_name, "creator_id": creator_id})
    db.session.commit()

def delete_student(student_id):
    sql = "DELETE FROM students WHERE id = :student_id"
    db.session.execute(text(sql), {"student_id": student_id})
    db.session.commit()

def search_students(creator_id, search_query):
    sql = """
        SELECT id, name FROM students
        WHERE creator_id = :creator_id AND name ILIKE :search_query
    """
    students = db.session.execute(text(sql), {"creator_id": creator_id, "search_query": f"%{search_query}%"}).fetchall()
    return students