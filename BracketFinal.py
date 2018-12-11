from flask import Flask, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    bracket = db.relationship('Bracket', backref='owner')
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Bracket(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('owner.id'))
    size = db.Column(db.Integer)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/Bracket')
def bracket():
    return render_template("bracket.html")

@app.route('/addUserToBracket')
def add_user_to_bracket():
    return render_template("bracket.html")

@app.route('/Profile')
def profile():
    return render_template("profile.html")


if __name__ == '__main__':
    app.run()
