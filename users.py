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