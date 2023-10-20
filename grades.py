from db import db
from sqlalchemy.sql import text

def count_associations(student_id):
    sql = "SELECT COUNT(*) FROM course_students WHERE student_id = :student_id"
    return db.session.execute(text(sql), {"student_id": student_id}).fetchone()[0]

def get_course_students(course_id, creator_id):
    sql = """
        SELECT students.id, students.name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        WHERE course_students.course_id = :course_id AND creator_id = :creator_id
        ORDER BY students.name
    """
    return db.session.execute(text(sql), {"course_id": course_id, "creator_id": creator_id}).fetchall()

def delete_associations(course_id, student_ids):
    sql_delete_course_students = '''
        DELETE FROM course_students
        WHERE course_id = :course_id
        AND student_id = ANY(:student_ids_to_delete)
    '''
    db.session.execute(text(sql_delete_course_students), {"course_id": course_id, "student_ids_to_delete": student_ids})
    sql_delete_activity = '''
        DELETE FROM activity
        WHERE course_id = :course_id
        AND student_id = ANY(:student_ids_to_delete)
    '''
    db.session.execute(text(sql_delete_activity), {"course_id": course_id, "student_ids_to_delete": student_ids})
    db.session.commit()

def create_associations(course_id, student_id):
    sql_insert1 = "INSERT INTO course_students (course_id, student_id) VALUES (:course_id, :student_id)"
    sql_insert2 = "INSERT INTO activity (course_id, student_id, activity_date) VALUES (:course_id, :student_id, '1900-01-01')"
    db.session.execute(text(sql_insert1), {"course_id": course_id, "student_id": student_id})
    db.session.execute(text(sql_insert2), {"course_id": course_id, "student_id": student_id})
    db.session.commit()

def set_grades(course_id, student_id, grade):
    sql_update = """
        UPDATE course_students
        SET grade = :grade
        WHERE course_id = :course_id AND student_id = :student_id
    """
    db.session.execute(text(sql_update), {"course_id": int(course_id), "student_id": int(student_id), "grade": grade})
    db.session.commit()

def get_students_data(creator_id):
    sql = """
        SELECT students.id AS student_id, students.name AS student_name, course_students.grade, courses.id AS course_id, courses.name AS course_name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        LEFT JOIN courses ON course_students.course_id = courses.id
        WHERE students.creator_id = :creator_id
        ORDER BY courses.id, students.id
    """
    return db.session.execute(text(sql), {"creator_id": creator_id}).fetchall()