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

def get_activity_data(course_id, student_id):
    sql = """
            SELECT activity_date, activity_score
            FROM activity
            WHERE course_id = :course_id AND student_id = :student_id
        """
    return db.session.execute(text(sql), {"course_id": course_id, "student_id": student_id}).fetchall()

def get_course_name(course_id, creator_id):
    sql = "SELECT name FROM courses WHERE id = :course_id AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"course_id": course_id, "creator_id": creator_id}).fetchone()[0]

def get_course_id(course_name, creator_id):
    sql = "SELECT id FROM courses WHERE name = :name AND creator_id = :creator_id"
    return db.session.execute(text(sql), {"name": course_name, "creator_id": creator_id}).fetchone()

def get_all_courses(creator_id):
    sql = "SELECT id, name FROM courses WHERE creator_id = :creator_id ORDER BY name"
    return db.session.execute(text(sql), {"creator_id": creator_id}).fetchall()

def get_course_students(course_id, creator_id):
    sql = """
        SELECT students.id, students.name
        FROM students
        INNER JOIN course_students ON students.id = course_students.student_id
        WHERE course_students.course_id = :course_id AND creator_id = :creator_id
        ORDER BY students.name
    """
    return db.session.execute(text(sql), {"course_id": course_id, "creator_id": creator_id}).fetchall()

def create_course(course_name, creator_id):
    sql = "INSERT INTO courses (name, creator_id) VALUES (:name, :creator_id)"
    db.session.execute(text(sql), {"name": course_name, "creator_id": creator_id})
    db.session.commit()

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

def remove_course(course_id):
    sql_delete_associations = "DELETE FROM course_students WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_associations), {"course_id": course_id})
    sql_delete_activities = "DELETE FROM activity WHERE course_id = :course_id"
    db.session.execute(text(sql_delete_activities), {"course_id": course_id})
    sql_delete_course = "DELETE FROM courses WHERE id = :course_id"
    db.session.execute(text(sql_delete_course), {"course_id": course_id})
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

def update_activity(course_id, student_id, score, current_date):
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
    db.session.commit()

def set_activity(course_id, student_id, score, current_date):
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
    db.session.commit()

def get_students_and_courses(creator_id, current_date):
    sql = """
        SELECT students.id AS student_id, students.name AS student_name, MAX(activity.activity_date) AS day,
            activity.course_id AS course_id, courses.name AS course_name, 
            MAX(CASE WHEN activity.activity_date = :current_date THEN activity.activity_score ELSE -1 END) AS activity_score
        FROM students
        INNER JOIN activity ON students.id = activity.student_id
        LEFT JOIN courses ON activity.course_id = courses.id
        WHERE students.creator_id = :creator_id
        GROUP BY students.id, students.name, activity.course_id, courses.name
    """
    return db.session.execute(text(sql), {"creator_id": creator_id, "current_date": current_date}).fetchall()
