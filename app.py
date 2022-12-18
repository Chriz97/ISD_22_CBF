from flask import Flask, render_template, url_for, redirect, request # Flask Standard Libraries
from flask_sqlalchemy import SQLAlchemy # SQLALCHEMY to construct an SQLite Database for User Registration, Login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user # Flask Login Management
from flask_wtf import FlaskForm # Flask What the Forms for Login, Registration Form
from wtforms import StringField, PasswordField, SubmitField, EmailField # Fields
from wtforms.validators import InputRequired, Length, ValidationError # Validators for What the Forms
from flask_bcrypt import Bcrypt # Used to decrypt Passwords in the Database, is a security feature
from flask_mail import Mail, Message # Flask Mail Support ==> Confirmation Mail for a new user
import pyotp # For 2-Factor Authentication
import datetime # Used for the API
import requests # Used for the API
import json # Used for the API
import pandas as pd # Pandas to read Data from Files

# Initialization of the Flask App and Setting up the Database for the registration Form as well as Bcrypt to encrypt Passwords#
# Added the Mail Function too

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = '2220_0390390_ajkölfja_1940'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Yesterday's Date: Used to get the Stock Price from the Alphavantage API

date_today = datetime.date.today()
date_yesterday = date_today - datetime.timedelta(days=1)

# Setting up the Mail Module in Order to send an Email when the user creates an account.
# Module Name = Flask Mail, Imports needed: Mail, Message

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "chrise2012.mayer@gmail.com"
app.config["MAIL_PASSWORD"] = "kvhmvhpqedkittzp"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# Initialize the Login Manager according to Flask Login

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

# SQL-Code (SQLITE): Creation of the Database: Name, Username, Password, Name and Email are required for the sign-up process

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
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username is not unique. Please choose a different one.")

# Login Form Username and Password with Validators

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# Construct a Two-Factor Login Authentication Form with Usage of PYOTP and Google Authenticator
# Pyotp is used to create a Pseudo Random Number based on base 32 with 32 Digits to ensure security
@app.route("/login/2FACBF/")
def login_2fa():
    # generating random secret key for authentication
    secret_key_Cross_Border_Finance = pyotp.random_base32(32) # Random Key, Base 32, 32 Digits
    return render_template("login_2fa.html", secret=secret_key_Cross_Border_Finance)
@app.route("/login/2FACBF/", methods=["POST", "GET"])
def login_2fa_form():
    # Secret Key from User
    secret_CBF = request.form.get("secret")
    # Gett OPT (One Time Password)
    otp_CBF = int(request.form.get("otp"))

    # If Verified return user back to the Main Home Page, else restart process
    if pyotp.TOTP(secret_CBF).verify(otp_CBF):
        return redirect(url_for("hello_world"))
    else:
        return redirect(url_for("login_2fa"))



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('login_2fa_form'))
    return render_template('login.html', form=form)

# This will be used for the Paywall of the Website, Login Required for all Websites

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))

# Registration Form + User receives an email if he successfully created an account

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        msg = Message("Welcome to Cross Border Finance", sender="noreply@crossborderfinance.com", recipients=[form.email.data])
        msg.body = "Thanks for creating your account. You can now fully use the Cross Border Finance Website"
        mail.send(msg)
        db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('register.html', form=form)

# Code to return the main homepage
@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template("main.html")

# Get Data from Excel Sheet which has all necessary indicators derived from Microsoft Finance

filename_Stock_Indicators = r"Stocks_Indicators.xlsx"
df = pd.read_excel(filename_Stock_Indicators)

# Read the Excel Database which is used for the Stock Indicators and Create Pandas DataFrame and store in a List variable


list_ticker = list(df["Ticker"])
list_beta = list(df["Beta"])
list_employees = list(df["Employees"])
list_exchange = list(df["Exchange"])
list_name = list(df["Name"])
list_52_high = list(df["52_Week_High"])
list_52_low = list(df["52_Week_LOW"])
list_description = list(df["Description"])
list_volume = list(df["Volume"])
list_outstanding = list(df["Shares Outstanding"])
list_industry = list(df["Industry"])
list_headquarters = list(df["Headquarters"])
list_market_cap = list(df["Market Cap"])
list_1_year_target = list(df["1_Year_Price_Target"])
list_year_incorporated = list(df["Year_Inc"])
list_stock_price = list(df["Stock_Price"])

# The following lines of Code are used to direct users to the 30 Dow Jones Companies; Loading
# the Stock Information from the Excel Database and Connect the API calls to the HTML Template

@app.route("/MMM", methods=["GET"])
def MMM():
    url_Time_Series_MMM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MMM&apikey=M9YDWDBER8VD0BTV'
    r_MMM = requests.get(url_Time_Series_MMM)
    data_MMM = r_MMM.content
    data_json_MMM = json.loads(data_MMM)
    data_clean_MMM = data_json_MMM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_MMM = [list_ticker[0], list_beta[0], list_employees[0], list_exchange[0], list_name[0],
                          list_52_high[0], list_52_low[0], list_description[0], list_volume[0],
                          list_outstanding[0], list_industry[0], list_headquarters[0], list_market_cap[0],
                          list_1_year_target[0], list_year_incorporated[0], list_stock_price[0]]
    return render_template("3M.html", data_API_MMM=data_clean_MMM, data_indicators_MMM=list_indicators_MMM)

@app.route("/AXP", methods=["GET"])
#@login_required
def AXP():
    url_Time_Series_AXP = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MMM&apikey=M9YDWDBER8VD0BTV'
    r_AXP = requests.get(url_Time_Series_AXP)
    data_AXP = r_AXP.content
    data_json_AXP = json.loads(data_AXP)
    data_clean_AXP = data_json_AXP["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_AXP = [list_ticker[1], list_beta[1], list_employees[1], list_exchange[1], list_name[1],
                          list_52_high[1], list_52_low[1], list_description[1], list_volume[1],
                          list_outstanding[1], list_industry[1], list_headquarters[1], list_market_cap[1],
                          list_1_year_target[1], list_year_incorporated[1], list_stock_price[1]]
    return render_template("American Express.html", data_API_AXP=data_clean_AXP, data_indicators_AXP=list_indicators_AXP)

@app.route("/AMGN", methods=["GET"])
def AMGN():
    list_indicators_AMGN = [list_ticker[2], list_beta[2], list_employees[2], list_exchange[2], list_name[2],
                          list_52_high[2], list_52_low[2], list_description[2], list_volume[2],
                          list_outstanding[2], list_industry[2], list_headquarters[2], list_market_cap[2],
                          list_1_year_target[2], list_year_incorporated[2], list_stock_price[2]]
    return render_template("Amgen.html", data_indicators_AMGN=list_indicators_AMGN)

@app.route("/AAPL", methods=["GET"])
def AAPL():
    list_indicators_AAPL = [list_ticker[3], list_beta[3], list_employees[3], list_exchange[3], list_name[3],
                          list_52_high[3], list_52_low[3], list_description[3], list_volume[3],
                          list_outstanding[3], list_industry[3], list_headquarters[3], list_market_cap[3],
                          list_1_year_target[3], list_year_incorporated[3], list_stock_price[3]]
    return render_template("Apple.html", data_indicators_AAPL=list_indicators_AAPL)

@app.route("/BA", methods=["GET"])
def BA():
    list_indicators_BA = [list_ticker[4], list_beta[4], list_employees[4], list_exchange[4], list_name[4],
                          list_52_high[4], list_52_low[4], list_description[4], list_volume[4],
                          list_outstanding[4], list_industry[4], list_headquarters[4], list_market_cap[4],
                          list_1_year_target[4], list_year_incorporated[4], list_stock_price[4]]
    return render_template("Boeing.html", data_indicators_BA=list_indicators_BA)

@app.route("/CAT", methods=["GET"])
def CAT():
    list_indicators_CAT = [list_ticker[5], list_beta[5], list_employees[5], list_exchange[5], list_name[5],
                          list_52_high[5], list_52_low[5], list_description[5], list_volume[5],
                          list_outstanding[5], list_industry[5], list_headquarters[5], list_market_cap[5],
                          list_1_year_target[5], list_year_incorporated[5],list_stock_price[5]]
    return render_template("Caterpillar.html", data_indicators_CAT=list_indicators_CAT)

    return render_template("Caterpillar.html")

@app.route("/CVX", methods=["GET"])
def CVX():
    list_indicators_CVX = [list_ticker[6], list_beta[6], list_employees[6], list_exchange[6], list_name[6],
                          list_52_high[6], list_52_low[6], list_description[6], list_volume[6],
                          list_outstanding[6], list_industry[6], list_headquarters[6], list_market_cap[6],
                          list_1_year_target[6], list_year_incorporated[6], list_stock_price[6]]
    return render_template("Chevron.html", data_indicators_CVX=list_indicators_CVX)

@app.route("/CSCO", methods=["GET"])
def CSCO():
    list_indicators_CSCO = [list_ticker[7], list_beta[7], list_employees[7], list_exchange[7], list_name[7],
                          list_52_high[7], list_52_low[7], list_description[7], list_volume[7],
                          list_outstanding[7], list_industry[7], list_headquarters[7], list_market_cap[7],
                          list_1_year_target[7], list_year_incorporated[7], list_stock_price[7]]
    return render_template("Cisco.html", data_indicators_CSCO=list_indicators_CSCO)

@app.route("/KO", methods=["GET"])
def KO():
    list_indicators_KO = [list_ticker[8], list_beta[8], list_employees[8], list_exchange[8], list_name[8],
                          list_52_high[8], list_52_low[8], list_description[8], list_volume[8],
                          list_outstanding[8], list_industry[8], list_headquarters[8], list_market_cap[8],
                          list_1_year_target[8], list_year_incorporated[8], list_stock_price[8]]
    return render_template("Coca-Cola.html", data_indicators_KO=list_indicators_KO)

@app.route("/DOW", methods=["GET"])
def DOW():
    list_indicators_DOW = [list_ticker[9], list_beta[9], list_employees[9], list_exchange[9], list_name[9],
                          list_52_high[9], list_52_low[9], list_description[9], list_volume[9],
                          list_outstanding[9], list_industry[9], list_headquarters[9], list_market_cap[9],
                          list_1_year_target[9], list_year_incorporated[9], list_stock_price[9]]
    return render_template("Dow.html", data_indicators_DOW=list_indicators_DOW)

@app.route("/GS", methods=["GET"])
def GS():
    list_indicators_GS = [list_ticker[10], list_beta[10], list_employees[10], list_exchange[10], list_name[10],
                          list_52_high[10], list_52_low[10], list_description[10], list_volume[10],
                          list_outstanding[10], list_industry[10], list_headquarters[10], list_market_cap[10],
                          list_1_year_target[10], list_year_incorporated[10], list_stock_price[10]]
    return render_template("Goldman Sachs.html", data_indicators_GS=list_indicators_GS)

@app.route("/HD", methods=["GET"])
def HD():
    list_indicators_HD = [list_ticker[11], list_beta[11], list_employees[11], list_exchange[11], list_name[11],
                           list_52_high[11], list_52_low[11], list_description[11], list_volume[11],
                           list_outstanding[11], list_industry[11], list_headquarters[11], list_market_cap[11],
                           list_1_year_target[11], list_year_incorporated[11], list_stock_price[11]]
    return render_template("Home Depot.html", data_indicators_HD=list_indicators_HD)

@app.route("/HON", methods=["GET"])
def HON():
    list_indicators_HON = [list_ticker[12], list_beta[12], list_employees[12], list_exchange[12], list_name[12],
                           list_52_high[12], list_52_low[12], list_description[12], list_volume[12],
                           list_outstanding[12], list_industry[12], list_headquarters[12], list_market_cap[12],
                           list_1_year_target[12], list_year_incorporated[12], list_stock_price[12]]
    return render_template("Honeywell.html", data_indicators_HON=list_indicators_HON)

@app.route("/INTC", methods=["GET"])
def INTC():
    list_indicators_INTC = [list_ticker[13], list_beta[13], list_employees[13], list_exchange[13], list_name[13],
                           list_52_high[13], list_52_low[13], list_description[13], list_volume[13],
                           list_outstanding[13], list_industry[13], list_headquarters[13], list_market_cap[13],
                           list_1_year_target[13], list_year_incorporated[13], list_stock_price[13]]
    return render_template("Intel.html", data_indicators_INTC=list_indicators_INTC)

@app.route("/IBM", methods=["GET"])
def IBM():
    url_Time_Series_IBM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=M9YDWDBER8VD0BTV'
    r_IBM = requests.get(url_Time_Series_IBM)
    data_IBM = r_IBM.content
    data_json_IBM = json.loads(data_IBM)
    data_clean_IBM = data_json_IBM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_IBM = [list_ticker[14], list_beta[14], list_employees[14], list_exchange[14], list_name[14],
                           list_52_high[14], list_52_low[14], list_description[14], list_volume[14],
                           list_outstanding[14], list_industry[14], list_headquarters[14], list_market_cap[14],
                           list_1_year_target[14], list_year_incorporated[14]]
    return render_template("IBM.html", data=data_clean_IBM, data_indicators_IBM=list_indicators_IBM)

@app.route("/JNJ", methods=["GET"])
def JNJ():
    list_indicators_JNJ = [list_ticker[15], list_beta[15], list_employees[15], list_exchange[15], list_name[15],
                           list_52_high[15], list_52_low[15], list_description[15], list_volume[15],
                           list_outstanding[15], list_industry[15], list_headquarters[15], list_market_cap[15],
                           list_1_year_target[15], list_year_incorporated[15], list_stock_price[15]]
    return render_template("Johnson and Johnson.html", data_indicators_JNJ=list_indicators_JNJ)

@app.route("/JPM", methods=["GET"])
def JPM():
    list_indicators_JPM = [list_ticker[16], list_beta[16], list_employees[16], list_exchange[16], list_name[16],
                           list_52_high[16], list_52_low[16], list_description[16], list_volume[16],
                           list_outstanding[16], list_industry[16], list_headquarters[16], list_market_cap[16],
                           list_1_year_target[16], list_year_incorporated[16], list_stock_price[16]]
    return render_template("JPMorgan Chase.html", data_indicators_JMP=list_indicators_JPM)

@app.route("/MCD", methods=["GET"])
def MCD():
    list_indicators_MCD = [list_ticker[17], list_beta[17], list_employees[17], list_exchange[17], list_name[17],
                           list_52_high[17], list_52_low[17], list_description[17], list_volume[17],
                           list_outstanding[17], list_industry[17], list_headquarters[17], list_market_cap[17],
                           list_1_year_target[17], list_year_incorporated[17], list_stock_price[17]]
    return render_template("McDonalds.html", data_indicators_MCD=list_indicators_MCD)

@app.route("/MRK", methods=["GET"])
def MRK():
    list_indicators_MRK = [list_ticker[18], list_beta[18], list_employees[18], list_exchange[18], list_name[18],
                           list_52_high[18], list_52_low[18], list_description[18], list_volume[18],
                           list_outstanding[18], list_industry[18], list_headquarters[18], list_market_cap[18],
                           list_1_year_target[18], list_year_incorporated[18], list_stock_price[18]]
    return render_template("Merck.html", data_indicators_MRK=list_indicators_MRK)

@app.route("/MSFT", methods=["GET"])
def MSFT():
    list_indicators_MSFT = [list_ticker[19], list_beta[19], list_employees[19], list_exchange[19], list_name[19],
                           list_52_high[19], list_52_low[19], list_description[19], list_volume[19],
                           list_outstanding[19], list_industry[19], list_headquarters[19], list_market_cap[19],
                           list_1_year_target[19], list_year_incorporated[19], list_stock_price[19]]
    return render_template("Microsoft.html", data_indicators_MSFT=list_indicators_MSFT)

@app.route("/NKE", methods=["GET"])
def NKE():
    list_indicators_NKE = [list_ticker[20], list_beta[20], list_employees[20], list_exchange[20], list_name[20],
                           list_52_high[20], list_52_low[20], list_description[20], list_volume[20],
                           list_outstanding[20], list_industry[20], list_headquarters[20], list_market_cap[20],
                           list_1_year_target[20], list_year_incorporated[20], list_stock_price[20]]
    return render_template("Nike.html", data_indicators_NKE=list_indicators_NKE)

@app.route("/PG", methods=["GET"])
def PG():
    list_indicators_PG = [list_ticker[21], list_beta[21], list_employees[21], list_exchange[21], list_name[21],
                           list_52_high[21], list_52_low[21], list_description[21], list_volume[21],
                           list_outstanding[21], list_industry[21], list_headquarters[21], list_market_cap[21],
                           list_1_year_target[21], list_year_incorporated[21], list_stock_price[21]]
    return render_template("Procter and Gamble.html", data_indicators_PG=list_indicators_PG)

@app.route("/CRM", methods=["GET"])
def CRM():
    list_indicators_CRM = [list_ticker[22], list_beta[22], list_employees[22], list_exchange[22], list_name[22],
                           list_52_high[22], list_52_low[22], list_description[22], list_volume[22],
                           list_outstanding[22], list_industry[22], list_headquarters[22], list_market_cap[22],
                           list_1_year_target[22], list_year_incorporated[22], list_stock_price[22]]
    return render_template("Salesforce.html", data_indicators_CRM=list_indicators_CRM)

@app.route("/TRV", methods=["GET"])
def TRV():
    list_indicators_TRV = [list_ticker[23], list_beta[23], list_employees[23], list_exchange[23], list_name[23],
                           list_52_high[23], list_52_low[23], list_description[23], list_volume[23],
                           list_outstanding[23], list_industry[23], list_headquarters[23], list_market_cap[23],
                           list_1_year_target[23], list_year_incorporated[23], list_stock_price[23]]
    return render_template("Travelers.html", data_indicators_TRV=list_indicators_TRV)

@app.route("/UNH", methods=["GET"])
def UNH():
    list_indicators_UNH = [list_ticker[24], list_beta[24], list_employees[24], list_exchange[24], list_name[24],
                           list_52_high[24], list_52_low[24], list_description[24], list_volume[24],
                           list_outstanding[24], list_industry[24], list_headquarters[24], list_market_cap[24],
                           list_1_year_target[24], list_year_incorporated[24], list_stock_price[24]]
    return render_template("United Health.html", data_indicators_UNH=list_indicators_UNH)

@app.route("/VZ", methods=["GET"])
def VZ():
    list_indicators_VZ = [list_ticker[25], list_beta[25], list_employees[25], list_exchange[25], list_name[25],
                           list_52_high[25], list_52_low[25], list_description[25], list_volume[25],
                           list_outstanding[25], list_industry[25], list_headquarters[25], list_market_cap[25],
                           list_1_year_target[25], list_year_incorporated[25], list_stock_price[25]]
    return render_template("Verizon.html", data_indicators_VZ=list_indicators_VZ)

@app.route("/V", methods=["GET"])
def V():
    list_indicators_V = [list_ticker[26], list_beta[26], list_employees[26], list_exchange[26], list_name[26],
                           list_52_high[26], list_52_low[26], list_description[26], list_volume[26],
                           list_outstanding[26], list_industry[26], list_headquarters[26], list_market_cap[26],
                           list_1_year_target[26], list_year_incorporated[26], list_stock_price[26]]
    return render_template("Visa.html", data_indicators_V=list_indicators_V)

@app.route("/WBA", methods=["GET"])
def WBA():
    list_indicators_WBA = [list_ticker[27], list_beta[27], list_employees[27], list_exchange[27], list_name[27],
                           list_52_high[27], list_52_low[27], list_description[27], list_volume[27],
                           list_outstanding[27], list_industry[27], list_headquarters[27], list_market_cap[27],
                           list_1_year_target[27], list_year_incorporated[27], list_stock_price[27]]
    return render_template("Walgreens Boots Alliance.html", data_indicators_WBA=list_indicators_WBA)

@app.route("/WMT", methods=["GET"])
def WMT():
    list_indicators_WMT = [list_ticker[28], list_beta[28], list_employees[28], list_exchange[28], list_name[28],
                           list_52_high[28], list_52_low[28], list_description[28], list_volume[28],
                           list_outstanding[28], list_industry[28], list_headquarters[28], list_market_cap[28],
                           list_1_year_target[28], list_year_incorporated[28], list_stock_price[28]]
    return render_template("Walmart.html", data_indicators_WMT=list_indicators_WMT)

@app.route("/DIS", methods=["GET"])
def DIS():
    list_indicators_DIS = [list_ticker[29], list_beta[29], list_employees[29], list_exchange[29], list_name[29],
                           list_52_high[29], list_52_low[29], list_description[29], list_volume[29],
                           list_outstanding[29], list_industry[29], list_headquarters[29], list_market_cap[29],
                           list_1_year_target[29], list_year_incorporated[29], list_stock_price[29]]
    return render_template("Walt Disney.html", data_indicators_DIS=list_indicators_DIS)

# Initialize the Flask APP with app.run

if __name__ == '__main__':
    app.run()
