from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from random import randint
app = Flask(__name__)

login = LoginManager(app)
login.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///UserInvoices.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoices = db.relationship('Invoice', backref='user')
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    balance = db.Column(db.Integer)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.set_balance(randint(50, 10000))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def set_balance(self, balance):
        self.balance = balance

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.username'))
    recipient = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Integer)

    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount


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


@login_required
@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=True)
    else:
        return render_template('home.html', user=False)

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
        login_user(user)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('profile'))
    return render_template('register.html', title='Register', form=form)


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
    if user is not None:
        if user.password == password:
            print("Loging in")
            login_user(user)
            return redirect(url_for('profile'))

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
    charges = Invoice.query.filter_by(sender=current_user.username).all()
    bills = Invoice.query.filter_by(recipient=current_user.username).all()
    balance = current_user.balance
    name = current_user.username
    return render_template("profile.html", charges=charges, bills=bills, balance=balance, name = name)


@app.route('/invoice/<id>', methods=['GET', 'POST'])
@login_required
def invoice(id):
    users = User.query.all()
    if id == '-99':
        return render_template('invoice.html', update=False, users=users)
    else:
        invoice = Invoice.query.filter_by(id=id).first()
        return render_template('invoice.html', update=True, invoice=invoice, users=users)


@app.route('/update_invoice/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    invoice= Invoice.query.filter_by(id=id).first()
    data= request.form
    invoice.recipient = data['recipient']
    invoice.amount = data['amount']
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    invoice= Invoice.query.filter_by(id=id).first()
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/create_invoice', methods=['GET', 'POST'])
@login_required
def create_invoice():
    data = request.form
    invoice = Invoice(current_user.username, data['recipient'], data['amount'])
    db.session.add(invoice)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/pay/<id>')
@login_required
def pay(id):
    invoice= Invoice.query.filter_by(id=id).first()
    sender = User.query.filter_by(username=invoice.sender).first()
    current_user.balance -= invoice.amount
    sender.balance += invoice.amount
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run()
