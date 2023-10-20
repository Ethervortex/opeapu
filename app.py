"""
This module initializes a Flask web application and sets a secret key.

Author: Teemu Ruokokoski
"""
from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import routes
