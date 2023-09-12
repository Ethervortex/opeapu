from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///teeruoko"
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")