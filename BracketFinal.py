from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)

login = LoginManager(app)
login.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UserBracket.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brackets = db.relationship('Bracket', backref='user')
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)


class Bracket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    size = db.Column(db.Integer)
    table_data = db.Column(db.String(800))


@login_required
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return render_template('profile.html', id=user.id)
    return render_template('register.html', title='Register', form=form)


@app.route('/Bracket/{{id}}')
def bracket(id):

    return render_template("bracket.html")


@app.route('/addUserToBracket/{{name}}')
def add_user_to_bracket(name):
    return render_template("bracket.html")


@login.user_loader
def load_user(uid):
    return User.query.get(uid)


@app.route('/login', methods=['GET', 'POST'])
def load_login():
    return render_template('login.html')


@app.route('/logingIn', methods=['POST'])
def submit_login():
    print("attempting to log in user")
    data = request.form
    password = data['password']
    name = data['name']
    user = User.query.filter_by(username=name).first()
    if user.password == password:
        print("loging in")
        login_user(user)
        return render_template('profile.html')
    else:
        print("auth failed")
        flash("Authentication Failed")
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/Profile')
@login_required
def profile():
    return render_template("profile.html")


if __name__ == '__main__':
    app.run()
