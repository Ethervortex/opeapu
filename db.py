"""
This module sets up the SQLAlchemy database URI from the environment variable
DATABASE_URL and creates a SQLAlchemy database instance.

Author: Teemu Ruokokoski
"""
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
