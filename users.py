"""
This is a module for defining the SQL queries to users-table.

Author: Teemu Ruokokoski
"""
from sqlalchemy.sql import text
from db import db

def create_user(username, hash_value):
    """ Create a new user in the database. """
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(text(sql), {"username":username, "password":hash_value})
    db.session.commit()
    return "User created"

def get_user(username):
    """ Retrieve user information by username. """
    sql = "SELECT id, password FROM users WHERE username = :username"
    return db.session.execute(text(sql), {"username": username}).fetchone()
