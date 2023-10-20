"""
This is a module for defining the SQL queries to students-table.

Author: Teemu Ruokokoski
"""
from sqlalchemy.sql import text
from db import db

def get_activity_data(course_id, student_id):
    """ Retrieve activity data for a specific course and student. """
    sql = """
            SELECT activity_date, activity_score
            FROM activity
            WHERE course_id = :course_id AND student_id = :student_id
        """
    activity_data = db.session.execute(
        text(sql),
        {"course_id": course_id, "student_id": student_id}
    ).fetchall()
    return activity_data

def update_activity(course_id, student_id, score, current_date):
    """ Update activity for a specific course and student. """
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
    """ Set activity for a specific course and student. """
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
    """ Retrieve student and course data for a creator on a specific date. """
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
    data = db.session.execute(
        text(sql),
        {"creator_id": creator_id, "current_date": current_date}
    ).fetchall()
    return data

def calculate_scores(activity_data):
    """ Calculate mean scores and absence from activity data. """
    total_score = 0
    absence = 0  # Count of -1 scores
    for act in activity_data:
        if act.activity_score is None:
            break
        if act.activity_score != -1:
            total_score += act.activity_score
        else:
            absence += 1

    mean_score = None
    if len(activity_data) - absence > 0:
        mean_score = total_score / (len(activity_data) - absence)
        mean_score = round(mean_score, 1)
    return mean_score, absence
