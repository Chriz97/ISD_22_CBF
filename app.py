import requests
import json
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# Initialization of the Flask App and Setting up the Database for the registration Form as well as Bcrypt to encrypt Passwords

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Creating the Entity and the Attributes of the Database Schema
@app.before_first_request # Not an error: Decorator is no usable after Flask Version 2.3.
def create_tables():
     db.create_all()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# SQL-Code: Creation of the Database, Username, Password, Name, Email and Date of birth are required for the sign up process

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    username = db.Column(db.String(10), nullable=True, unique=True) # 10 Characters max for username
    password = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(50), nullable=True, unique=True)

# Registration Form: First Name, Last Name, Username, Password, Email, Date of birth + Validators and Render_KW

class RegisterForm(FlaskForm):

    first_name = StringField(validators=[InputRequired(), Length(min=3, max=50)], render_kw={"placeholder": "First Name"})

    last_name = StringField(validators=[InputRequired(), Length(min=3, max=50)], render_kw={"placeholder": "Last Name"})

    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "New Password"})

    email = EmailField(validators=[InputRequired()], render_kw={"placeholder": "Email"})

    submit = SubmitField('Sign up now')

# Validate whether a Username is already in use or unique
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username is not unique. Please choose a different one.")

# Login Form Username and Password with Validators

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# Validate Login and Redirect the User the Homepage

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('hello_world'))
    return render_template('login.html', form=form)

# This will be used for the Paywall of the Website, Login Required for all Websites

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('register.html', form=form)

# Code to return the main homepage
@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template("main.html")

# The following lines of Code are used to direct users to the 30 Dow Jones Companies

@app.route("/MMM", methods=["GET"])
def MMM():
    return render_template("3M.html")

@app.route("/AXP", methods=["GET"])
@login_required
def AXP():
    return render_template("American Express.html")

@app.route("/AMGN", methods=["GET"])
def AMGN():
    return render_template("Amgen.html")

@app.route("/AAPL", methods=["GET"])
def AAPL():
    return render_template("Apple.html")

@app.route("/BA", methods=["GET"])
def BA():
    return render_template("Boeing.html")

@app.route("/CAT", methods=["GET"])
def CAT():
    return render_template("Caterpillar.html")

@app.route("/CVX", methods=["GET"])
def CVX():
    return render_template("Chevron.html")

@app.route("/CSCO", methods=["GET"])
def CSCO():
    return render_template("Cisco.html")

@app.route("/KO", methods=["GET"])
def KO():
    return render_template("Coca-Cola.html")

@app.route("/DOW", methods=["GET"])
def DOW():
    return render_template("Dow.html")

@app.route("/GS", methods=["GET"])
def GS():
    return render_template("Goldman Sachs.html")

@app.route("/HD", methods=["GET"])
def HD():
    return render_template("Home Depot.html")

@app.route("/HON", methods=["GET"])
def HON():
    return render_template("Honeywell.html")

@app.route("/INTC", methods=["GET"])
def INTC():
    return render_template("Intel.html")

@app.route("/IBM", methods=["GET"])
def IBM():
    url_Time_Series_DBK = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=M9YDWDBER8VD0BTV'
    r_DBK = requests.get(url_Time_Series_DBK)
    data = r_DBK.content
    data_json1 = json.loads(data)
    data_clean1 = data_json1["Time Series (Daily)"]["2022-11-03"]["4. close"]
    return render_template("IBM.html", data=data_clean1)

@app.route("/JNJ", methods=["GET"])
def JNJ():
    return render_template("Johnson and Johnson.html")

@app.route("/JPM", methods=["GET"])
def JPM():
    return render_template("JPMorgan Chase.html")

@app.route("/MCD", methods=["GET"])
def MCD():
    return render_template("McDonalds.html")

@app.route("/MRK", methods=["GET"])
def MRK():
    return render_template("Merck.html")

@app.route("/MSFT", methods=["GET"])
def MSFT():
    return render_template("Microsoft.html")

@app.route("/NKE", methods=["GET"])
def NKE():
    return render_template("Nike.html")

@app.route("/PG", methods=["GET"])
def PG():
    return render_template("Procter and Gamble.html")

@app.route("/CRM", methods=["GET"])
def CRM():
    return render_template("Salesforce.html")

@app.route("/TRV", methods=["GET"])
def TRV():
    return render_template("Travelers.html")

@app.route("/UNH", methods=["GET"])
def UNH():
    return render_template("United Health.html")

@app.route("/VZ", methods=["GET"])
def VZ():
    return render_template("Verizon.html")

@app.route("/V", methods=["GET"])
def V():
    return render_template("Visa.html")

@app.route("/WBA", methods=["GET"])
def WBA():
    return render_template("Walgreens Boots Alliance.html")

@app.route("/WMT", methods=["GET"])
def WMT():
    return render_template("Walmart.html")

@app.route("/DIS", methods=["GET"])
def DIS():
    return render_template("Walt Disney.html")

# Initialize the Flask APP with app.run

if __name__ == '__main__':
    app.run()
