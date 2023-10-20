"""
This is a module for defining the SQL queries to students-table.

Author: Teemu Ruokokoski
"""
from sqlalchemy.sql import text
from db import db

def get_student_id(student_name, creator_id):
    """ Retrieve the ID of a student by name and creator ID. """
    sql = "SELECT id FROM students WHERE name = :name AND creator_id = :creator_id"
    student_ids = db.session.execute(
        text(sql),
        {"name": student_name, "creator_id": creator_id}
    ).fetchone()
    return student_ids

def get_student_name(student_id, creator_id):
    """ Retrieve the name of a student by ID and creator ID. """
    sql = "SELECT name FROM students WHERE id = :student_id AND creator_id = :creator_id"
    student_names = db.session.execute(
        text(sql),
        {"student_id": student_id, "creator_id": creator_id}
    ).fetchone()[0]
    return student_names

def get_all_students(creator_id):
    """ Retrieve all students for a given creator. """
    sql = "SELECT id, name FROM students WHERE creator_id = :creator_id ORDER BY name"
    return db.session.execute(text(sql), {"creator_id": creator_id}).fetchall()

def create_student(student_name, creator_id):
    """ Create a new student in the database. """
    sql = "INSERT INTO students (name, creator_id) VALUES (:name, :creator_id)"
    db.session.execute(text(sql), {"name": student_name, "creator_id": creator_id})
    db.session.commit()

def delete_student(student_id):
    """ Delete a student from the database by ID. """
    sql = "DELETE FROM students WHERE id = :student_id"
    db.session.execute(text(sql), {"student_id": student_id})
    db.session.commit()

def search_students(creator_id, search_query):
    """ Search for students by name, matching a search query. """
    sql = """
        SELECT id, name FROM students
        WHERE creator_id = :creator_id AND name ILIKE :search_query
    """
    students = db.session.execute(
        text(sql),
        {"creator_id": creator_id, "search_query": f"%{search_query}%"}
    ).fetchall()
    return students
