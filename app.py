from flask import Flask, render_template, url_for, redirect, request # Flask Standard Libraries
from flask_sqlalchemy import SQLAlchemy # SQLALCHEMY to construct an SQLite Database for User Registration, Login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user # Flask Login Management
from flask_wtf import FlaskForm # Flask What the Forms for Login, Registration Form
from wtforms import StringField, PasswordField, SubmitField, EmailField # Fields
from wtforms.validators import InputRequired, Length, ValidationError # Validators for What the Forms
from flask_bcrypt import Bcrypt # Used to decrypt Passwords in the Database, is a security feature
from flask_mail import Mail, Message # Flask Mail Support ==> Confirmation Mail for a new user
import pyotp  # For 2-Factor Authentication
import requests  # Used for the API
import json  # Used for the API
import pandas as pd  # Pandas to read Data from Files
import datetime # Used to Determine Yesterday's Date
import holidays # Used to Determine whether yesterday is a federal holiday in the United States

# Initialization of the Flask App and Setting up the Database for the registration Form as well as Bcrypt to encrypt Passwords
# and the Flask Mail Module to send users a Welcome Message after a successful Sign-Up Process

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = '2220_0390390_ajkölfja_1940'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Yesterday's Date Variable: Used to get the Stock Price from the Alphavantage API
# Created the is_trading_day to determine whether yesterday is a trading.
# If not: The while loop continues to expand the timedelta until a trading day is reached
# Function: is_trading_day returns True in this case.

date_today = datetime.date.today()
delta_today = 1
date_yesterday = str(date_today - datetime.timedelta(days=delta_today))

def is_trading_day(date_yesterday):
    # Convert the input date to a datetime object
    date = datetime.datetime.strptime(date_yesterday, '%Y-%m-%d')
    # Create a holidays object for the specified country
    hdays = holidays.US()
    # Check if the day is a weekday and not a holiday
    return date.isoweekday() in range(1, 6) and date not in hdays

while is_trading_day(date_yesterday) == False:
    delta_today += 1
    date_yesterday = str(date_today - datetime.timedelta(days=delta_today))

# Setting up the Mail Module in Order to send an Email when the user creates an account.
# Module Name = Flask Mail, Imports needed: Mail, Message

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "chrise2012.mayer@gmail.com"
app.config["MAIL_PASSWORD"] = "kvhmvhpqedkittzp"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# Initialize the Login Manager according to the Flask Login Documentation

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Creating the Table (Entity) and the Attributes of the Database Schema
@app.before_first_request # Not an error: Decorator is not usable after Flask Version 2.3.
def create_tables():
     db.create_all()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# SQL-Code (SQLITE): Creation of the Database: Name, Username, Password, Name and Email are required for the Sign-Up process
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    username = db.Column(db.String(10), unique=True)  # 10 Characters max for username
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)

# Registration Form: First Name, Last Name, Username, Password, Email, Date of birth + Validators and Render_KW

class RegisterForm(FlaskForm):

    first_name = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "First Name"})

    last_name = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Last Name"})

    username = StringField(validators=[InputRequired(), Length(min=4, max=10)], render_kw={"placeholder": "Username"})

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

    submit = SubmitField("Continue to 2FA")

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
        msg = Message("Welcome to Cross Border Finance", sender="chrise2012.mayer@gmail.com", recipients=[form.email.data])
        msg.body = "Thanks for creating your account. You can now fully experience the Cross Border Finance Website. " \
                   "Please see the attached PDF Guide for further information on the website."
        with app.open_resource("User_Guide_Cross_Border_Finance.pdf") as attachment:
            msg.attach("User_Guide_Cross_Border_Finance.pdf", "text/pdf", attachment.read())
        mail.send(msg)
        db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('register.html', form=form)

# Code for the Landing Page, Method=GET
@app.route("/", methods=["GET"])
def landing_page():
    return render_template("landing_page.html")

# Code for the Home Page, METHOD=GET
@app.route('/home', methods=["GET"])
def hello_world():
    return render_template("main.html")

# Get Data from Excel Sheet with all Shiller KGVs (CAPE in English), for the first graph (CAPE)

filename_Stock_CAPE = r"Shiller_KGV_full.xlsx"
df_CAPE = pd.read_excel(filename_Stock_CAPE)

# Excess Cape: Used for the second graph (Excess CAPE)

filename_EXC_adjusted = r"Excess_Cape_Full.xlsx"
df_EXC = pd.read_excel(filename_EXC_adjusted)

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
#@login_required
def MMM():
    url_Time_Series_MMM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MMM&apikey=B4UKNHORQ1AFHU68'
    r_MMM = requests.get(url_Time_Series_MMM)
    data_MMM = r_MMM.content
    data_json_MMM = json.loads(data_MMM)
    data_clean_MMM = data_json_MMM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_MMM = [list_ticker[0], list_beta[0], list_employees[0], list_exchange[0], list_name[0],
                          list_52_high[0], list_52_low[0], list_description[0], list_volume[0],
                          list_outstanding[0], list_industry[0], list_headquarters[0], list_market_cap[0],
                          list_1_year_target[0], list_year_incorporated[0], list_stock_price[0]]
    list_CAPE_MMM = list(df_CAPE["MMM"])
    list_EXC_MMM = list(df_EXC["MMM"])
    return render_template("3M.html", data_API_MMM=data_clean_MMM, data_indicators_MMM=list_indicators_MMM, data_CAPE_MMM=list_CAPE_MMM, data_EXC_MMM=list_EXC_MMM)

@app.route("/AXP", methods=["GET"])
@login_required
def AXP():
    url_Time_Series_AXP = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MMM&apikey=B4UKNHORQ1AFHU68'
    r_AXP = requests.get(url_Time_Series_AXP)
    data_AXP = r_AXP.content
    data_json_AXP = json.loads(data_AXP)
    data_clean_AXP = data_json_AXP["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_AXP = [list_ticker[1], list_beta[1], list_employees[1], list_exchange[1], list_name[1],
                          list_52_high[1], list_52_low[1], list_description[1], list_volume[1],
                          list_outstanding[1], list_industry[1], list_headquarters[1], list_market_cap[1],
                          list_1_year_target[1], list_year_incorporated[1], list_stock_price[1]]
    list_CAPE_AXP = list(df_CAPE["AXP"])
    list_EXC_AXP = list(df_EXC["AXP"])
    return render_template("American Express.html", data_API_AXP=data_clean_AXP, data_indicators_AXP=list_indicators_AXP, data_CAPE_AXP=list_CAPE_AXP, data_EXC_AXP=list_EXC_AXP)

@app.route("/AMGN", methods=["GET"])
@login_required
def AMGN():
    url_Time_Series_AMGN = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=AMGN&apikey=B4UKNHORQ1AFHU68'
    r_AMGN = requests.get(url_Time_Series_AMGN)
    data_AMGN = r_AMGN.content
    data_json_AMGN = json.loads(data_AMGN)
    data_clean_AMGN = data_json_AMGN["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_AMGN = [list_ticker[2], list_beta[2], list_employees[2], list_exchange[2], list_name[2],
                          list_52_high[2], list_52_low[2], list_description[2], list_volume[2],
                          list_outstanding[2], list_industry[2], list_headquarters[2], list_market_cap[2],
                          list_1_year_target[2], list_year_incorporated[2], list_stock_price[2]]
    list_CAPE_AMGN = list(df_CAPE["AMGN"])
    list_EXC_AMGN = list(df_EXC["AMGN"])
    return render_template("Amgen.html", data_API_AMGN=data_clean_AMGN,data_indicators_AMGN=list_indicators_AMGN, data_CAPE_AMGN=list_CAPE_AMGN, data_EXC_AMGN=list_EXC_AMGN)

@app.route("/AAPL", methods=["GET"])
def AAPL():
    url_Time_Series_AAPL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=AAPL&apikey=B4UKNHORQ1AFHU68'
    r_AAPL= requests.get(url_Time_Series_AAPL)
    data_AAPL = r_AAPL.content
    data_json_AAPL = json.loads(data_AAPL)
    data_clean_AAPL = data_json_AAPL["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_AAPL = [list_ticker[3], list_beta[3], list_employees[3], list_exchange[3], list_name[3],
                          list_52_high[3], list_52_low[3], list_description[3], list_volume[3],
                          list_outstanding[3], list_industry[3], list_headquarters[3], list_market_cap[3],
                          list_1_year_target[3], list_year_incorporated[3], list_stock_price[3]]
    list_CAPE_AAPL = list(df_CAPE["AAPL"])
    list_EXC_AAPL = list(df_EXC["AAPL"])
    return render_template("Apple.html", data_API_AAPL=data_clean_AAPL, data_indicators_AAPL=list_indicators_AAPL, data_CAPE_AAPL=list_CAPE_AAPL, data_EXC_AAPL=list_EXC_AAPL)

@app.route("/BA", methods=["GET"])
@login_required
def BA():
    url_Time_Series_BA = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=BA&apikey=B4UKNHORQ1AFHU68'
    r_BA = requests.get(url_Time_Series_BA)
    data_BA = r_BA.content
    data_json_BA = json.loads(data_BA)
    data_clean_BA = data_json_BA["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_BA = [list_ticker[4], list_beta[4], list_employees[4], list_exchange[4], list_name[4],
                          list_52_high[4], list_52_low[4], list_description[4], list_volume[4],
                          list_outstanding[4], list_industry[4], list_headquarters[4], list_market_cap[4],
                          list_1_year_target[4], list_year_incorporated[4], list_stock_price[4]]
    list_CAPE_BA = list(df_CAPE["BA"])
    list_EXC_BA = list(df_EXC["BA"])
    return render_template("Boeing.html", data_API_BA=data_clean_BA, data_indicators_BA=list_indicators_BA, data_CAPE_BA=list_CAPE_BA, data_EXC_BA=list_EXC_BA)

@app.route("/CAT", methods=["GET"])
@login_required
def CAT():
    url_Time_Series_CAT = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=CAT&apikey=B4UKNHORQ1AFHU68'
    r_CAT = requests.get(url_Time_Series_CAT)
    data_CAT = r_CAT.content
    data_json_CAT = json.loads(data_CAT)
    data_clean_CAT = data_json_CAT["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_CAT = [list_ticker[5], list_beta[5], list_employees[5], list_exchange[5], list_name[5],
                          list_52_high[5], list_52_low[5], list_description[5], list_volume[5],
                          list_outstanding[5], list_industry[5], list_headquarters[5], list_market_cap[5],
                          list_1_year_target[5], list_year_incorporated[5],list_stock_price[5]]
    list_CAPE_CAT = list(df_CAPE["CAT"])
    list_EXC_CAT = list(df_EXC["CAT"])
    return render_template("Caterpillar.html", data_API_CAT=data_clean_CAT, data_indicators_CAT=list_indicators_CAT, data_CAPE_CAT=list_CAPE_CAT, data_EXC_CAT=list_EXC_CAT)

@app.route("/CVX", methods=["GET"])
@login_required
def CVX():
    url_Time_Series_CVX = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=CVX&apikey=B4UKNHORQ1AFHU68'
    r_CVX = requests.get(url_Time_Series_CVX)
    data_CVX = r_CVX.content
    data_json_CVX = json.loads(data_CVX)
    data_clean_CVX = data_json_CVX["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_CVX = [list_ticker[6], list_beta[6], list_employees[6], list_exchange[6], list_name[6],
                          list_52_high[6], list_52_low[6], list_description[6], list_volume[6],
                          list_outstanding[6], list_industry[6], list_headquarters[6], list_market_cap[6],
                          list_1_year_target[6], list_year_incorporated[6], list_stock_price[6]]
    list_CAPE_CVX = list(df_CAPE["CVX"])
    list_EXC_CVX = list(df_EXC["CVX"])
    return render_template("Chevron.html", data_API_CVX=data_clean_CVX, data_indicators_CVX=list_indicators_CVX, data_CAPE_CVX=list_CAPE_CVX, data_EXC_CVX=list_EXC_CVX)

@app.route("/CSCO", methods=["GET"])
@login_required
def CSCO():
    url_Time_Series_CSCO = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=CSCO&apikey=B4UKNHORQ1AFHU68'
    r_CSCO = requests.get(url_Time_Series_CSCO)
    data_CSCO = r_CSCO.content
    data_json_CSCO = json.loads(data_CSCO)
    data_clean_CSCO = data_json_CSCO["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_CSCO = [list_ticker[7], list_beta[7], list_employees[7], list_exchange[7], list_name[7],
                          list_52_high[7], list_52_low[7], list_description[7], list_volume[7],
                          list_outstanding[7], list_industry[7], list_headquarters[7], list_market_cap[7],
                          list_1_year_target[7], list_year_incorporated[7], list_stock_price[7]]
    list_CAPE_CSCO = list(df_CAPE["CSCO"])
    list_EXC_CSCO = list(df_EXC["CSCO"])
    return render_template("Cisco.html", data_API_CSCO=data_clean_CSCO, data_indicators_CSCO=list_indicators_CSCO, data_CAPE_CSCO=list_CAPE_CSCO, data_EXC_CSCO=list_EXC_CSCO)

@app.route("/KO", methods=["GET"])
@login_required
def KO():
    url_Time_Series_KO = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=KO&apikey=B4UKNHORQ1AFHU68'
    r_KO= requests.get(url_Time_Series_KO)
    data_KO = r_KO.content
    data_json_KO = json.loads(data_KO)
    data_clean_KO = data_json_KO["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_KO = [list_ticker[8], list_beta[8], list_employees[8], list_exchange[8], list_name[8],
                          list_52_high[8], list_52_low[8], list_description[8], list_volume[8],
                          list_outstanding[8], list_industry[8], list_headquarters[8], list_market_cap[8],
                          list_1_year_target[8], list_year_incorporated[8], list_stock_price[8]]
    list_CAPE_KO = list(df_CAPE["KO"])
    list_EXC_KO = list(df_EXC["KO"])
    return render_template("Coca-Cola.html", data_API_KO=data_clean_KO, data_indicators_KO=list_indicators_KO, data_CAPE_KO=list_CAPE_KO, data_EXC_KO=list_EXC_KO)

@app.route("/DOW", methods=["GET"])
@login_required
def DOW():
    url_Time_Series_DOW = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=DOW&apikey=B4UKNHORQ1AFHU68'
    r_DOW = requests.get(url_Time_Series_DOW)
    data_DOW = r_DOW.content
    data_json_DOW = json.loads(data_DOW)
    data_clean_DOW = data_json_DOW["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_DOW = [list_ticker[9], list_beta[9], list_employees[9], list_exchange[9], list_name[9],
                          list_52_high[9], list_52_low[9], list_description[9], list_volume[9],
                          list_outstanding[9], list_industry[9], list_headquarters[9], list_market_cap[9],
                          list_1_year_target[9], list_year_incorporated[9], list_stock_price[9]]
    return render_template("Dow.html", data_API_DOW=data_clean_DOW, data_indicators_DOW=list_indicators_DOW)

@app.route("/GS", methods=["GET"])
@login_required
def GS():
    url_Time_Series_GS = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=GS&apikey=B4UKNHORQ1AFHU68'
    r_GS = requests.get(url_Time_Series_GS)
    data_GS = r_GS.content
    data_json_GS = json.loads(data_GS)
    data_clean_GS = data_json_GS["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_GS = [list_ticker[10], list_beta[10], list_employees[10], list_exchange[10], list_name[10],
                          list_52_high[10], list_52_low[10], list_description[10], list_volume[10],
                          list_outstanding[10], list_industry[10], list_headquarters[10], list_market_cap[10],
                          list_1_year_target[10], list_year_incorporated[10], list_stock_price[10]]
    return render_template("Goldman Sachs.html", data_API_GS=data_clean_GS, data_indicators_GS=list_indicators_GS)

@app.route("/HD", methods=["GET"])
@login_required
def HD():
    url_Time_Series_HD = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=HD&apikey=B4UKNHORQ1AFHU68'
    r_HD = requests.get(url_Time_Series_HD)
    data_HD = r_HD.content
    data_json_HD = json.loads(data_HD)
    data_clean_HD = data_json_HD["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_HD = [list_ticker[11], list_beta[11], list_employees[11], list_exchange[11], list_name[11],
                           list_52_high[11], list_52_low[11], list_description[11], list_volume[11],
                           list_outstanding[11], list_industry[11], list_headquarters[11], list_market_cap[11],
                           list_1_year_target[11], list_year_incorporated[11], list_stock_price[11]]
    list_CAPE_HD = list(df_CAPE["HD"])
    list_EXC_HD = list(df_EXC["HD"])
    return render_template("Home Depot.html", data_API_HD=data_clean_HD, data_indicators_HD=list_indicators_HD, data_CAPE_HD=list_CAPE_HD, data_EXC_HD=list_EXC_HD)

@app.route("/HON", methods=["GET"])
@login_required
def HON():
    url_Time_Series_HON = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=HON&apikey=B4UKNHORQ1AFHU68'
    r_HON = requests.get(url_Time_Series_HON)
    data_HON = r_HON.content
    data_json_HON = json.loads(data_HON)
    data_clean_HON = data_json_HON["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_HON = [list_ticker[12], list_beta[12], list_employees[12], list_exchange[12], list_name[12],
                           list_52_high[12], list_52_low[12], list_description[12], list_volume[12],
                           list_outstanding[12], list_industry[12], list_headquarters[12], list_market_cap[12],
                           list_1_year_target[12], list_year_incorporated[12], list_stock_price[12]]
    list_CAPE_HON = list(df_CAPE["HON"])
    list_EXC_HON = list(df_EXC["HON"])
    return render_template("Honeywell.html", data_API_HON=data_clean_HON, data_indicators_HON=list_indicators_HON, data_CAPE_HON=list_CAPE_HON, data_EXC_HON=list_EXC_HON)

@app.route("/INTC", methods=["GET"])
@login_required
def INTC():
    url_Time_Series_INTC = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=INTC&apikey=B4UKNHORQ1AFHU68'
    r_INTC = requests.get(url_Time_Series_INTC)
    data_INTC = r_INTC.content
    data_json_INTC = json.loads(data_INTC)
    data_clean_INTC = data_json_INTC["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_INTC = [list_ticker[13], list_beta[13], list_employees[13], list_exchange[13], list_name[13],
                           list_52_high[13], list_52_low[13], list_description[13], list_volume[13],
                           list_outstanding[13], list_industry[13], list_headquarters[13], list_market_cap[13],
                           list_1_year_target[13], list_year_incorporated[13], list_stock_price[13]]
    list_CAPE_INTC = list(df_CAPE["INTC"])
    list_EXC_INTC = list(df_EXC["INTC"])
    return render_template("Intel.html", data_API_INTC=data_clean_INTC, data_indicators_INTC=list_indicators_INTC, data_CAPE_INTC=list_CAPE_INTC, data_EXC_INTC=list_EXC_INTC)

@app.route("/IBM", methods=["GET"])
@login_required
def IBM():
    url_Time_Series_IBM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=B4UKNHORQ1AFHU68'
    r_IBM = requests.get(url_Time_Series_IBM)
    data_IBM = r_IBM.content
    data_json_IBM = json.loads(data_IBM)
    data_clean_IBM = data_json_IBM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_IBM = [list_ticker[14], list_beta[14], list_employees[14], list_exchange[14], list_name[14],
                           list_52_high[14], list_52_low[14], list_description[14], list_volume[14],
                           list_outstanding[14], list_industry[14], list_headquarters[14], list_market_cap[14],
                           list_1_year_target[14], list_year_incorporated[14]]
    list_CAPE_IBM = list(df_CAPE["IBM"])
    list_EXC_IBM = list(df_EXC["IBM"])
    return render_template("IBM.html", data_API_IBM=data_clean_IBM, data_indicators_IBM=list_indicators_IBM, data_CAPE_IBM=list_CAPE_IBM, data_EXC_IBM=list_EXC_IBM)

@app.route("/JNJ", methods=["GET"])
@login_required
def JNJ():
    url_Time_Series_JNJ = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=JNJ&apikey=B4UKNHORQ1AFHU68'
    r_JNJ = requests.get(url_Time_Series_JNJ)
    data_JNJ = r_JNJ.content
    data_json_JNJ = json.loads(data_JNJ)
    data_clean_JNJ = data_json_JNJ["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_JNJ = [list_ticker[15], list_beta[15], list_employees[15], list_exchange[15], list_name[15],
                           list_52_high[15], list_52_low[15], list_description[15], list_volume[15],
                           list_outstanding[15], list_industry[15], list_headquarters[15], list_market_cap[15],
                           list_1_year_target[15], list_year_incorporated[15], list_stock_price[15]]
    list_CAPE_JNJ = list(df_CAPE["JNJ"])
    list_EXC_JNJ = list(df_EXC["JNJ"])
    return render_template("Johnson and Johnson.html", data_API_JNJ=data_clean_JNJ, data_indicators_JNJ=list_indicators_JNJ, data_CAPE_JNJ=list_CAPE_JNJ, data_EXC_JNJ=list_EXC_JNJ)

@app.route("/JPM", methods=["GET"])
@login_required
def JPM():
    url_Time_Series_JPM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=JPM&apikey=B4UKNHORQ1AFHU68'
    r_JPM = requests.get(url_Time_Series_JPM)
    data_JPM = r_JPM.content
    data_json_JPM = json.loads(data_JPM)
    data_clean_JPM = data_json_JPM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_JPM = [list_ticker[16], list_beta[16], list_employees[16], list_exchange[16], list_name[16],
                           list_52_high[16], list_52_low[16], list_description[16], list_volume[16],
                           list_outstanding[16], list_industry[16], list_headquarters[16], list_market_cap[16],
                           list_1_year_target[16], list_year_incorporated[16], list_stock_price[16]]
    list_CAPE_JPM = list(df_CAPE["JPM"])
    list_EXC_JPM =  list(df_EXC["JPM"])
    return render_template("JPMorgan Chase.html", data_API_JPM=data_clean_JPM, data_indicators_JMP=list_indicators_JPM, data_CAPE_JPM=list_CAPE_JPM, data_EXC_JPM=list_EXC_JPM)

@app.route("/MCD", methods=["GET"])
@login_required
def MCD():
    url_Time_Series_MCD = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MCD&apikey=B4UKNHORQ1AFHU68'
    r_MCD = requests.get(url_Time_Series_MCD)
    data_MCD = r_MCD.content
    data_json_MCD = json.loads(data_MCD)
    data_clean_MCD = data_json_MCD["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_MCD = [list_ticker[17], list_beta[17], list_employees[17], list_exchange[17], list_name[17],
                           list_52_high[17], list_52_low[17], list_description[17], list_volume[17],
                           list_outstanding[17], list_industry[17], list_headquarters[17], list_market_cap[17],
                           list_1_year_target[17], list_year_incorporated[17], list_stock_price[17]]
    list_CAPE_MCD = list(df_CAPE["MCD"])
    list_EXC_MCD =  list(df_EXC["MCD"])
    return render_template("McDonalds.html", data_API_MCD=data_clean_MCD, data_indicators_MCD=list_indicators_MCD, data_CAPE_MCD=list_CAPE_MCD, data_EXC_MCD=list_EXC_MCD)

@app.route("/MRK", methods=["GET"])
@login_required
def MRK():
    url_Time_Series_MRK = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MRK&apikey=B4UKNHORQ1AFHU68'
    r_MRK = requests.get(url_Time_Series_MRK)
    data_MRK = r_MRK.content
    data_json_MRK = json.loads(data_MRK)
    data_clean_MRK = data_json_MRK["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_MRK = [list_ticker[18], list_beta[18], list_employees[18], list_exchange[18], list_name[18],
                           list_52_high[18], list_52_low[18], list_description[18], list_volume[18],
                           list_outstanding[18], list_industry[18], list_headquarters[18], list_market_cap[18],
                           list_1_year_target[18], list_year_incorporated[18], list_stock_price[18]]
    list_CAPE_MRK = list(df_CAPE["MRK"])
    list_EXC_MRK =  list(df_EXC["MRK"])
    return render_template("Merck.html", data_API_MRK=data_clean_MRK, data_indicators_MRK=list_indicators_MRK, data_CAPE_MRK=list_CAPE_MRK, data_EXC_MRK=list_EXC_MRK)


@app.route("/MSFT", methods=["GET"])
@login_required
def MSFT():
    url_Time_Series_MSFT = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=B4UKNHORQ1AFHU68'
    r_MSFT = requests.get(url_Time_Series_MSFT)
    data_MSFT = r_MSFT.content
    data_json_MSFT = json.loads(data_MSFT)
    data_clean_MSFT = data_json_MSFT["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_MSFT = [list_ticker[19], list_beta[19], list_employees[19], list_exchange[19], list_name[19],
                           list_52_high[19], list_52_low[19], list_description[19], list_volume[19],
                           list_outstanding[19], list_industry[19], list_headquarters[19], list_market_cap[19],
                           list_1_year_target[19], list_year_incorporated[19], list_stock_price[19]]
    list_CAPE_MSFT = list(df_CAPE["MSFT"])
    list_EXC_MSFT =  list(df_EXC["MSFT"])
    return render_template("Microsoft.html", data_API_MSFT=data_clean_MSFT, data_indicators_MSFT=list_indicators_MSFT, data_CAPE_MSFT=list_CAPE_MSFT, data_EXC_MSFT=list_EXC_MSFT)

@app.route("/NKE", methods=["GET"])
@login_required
def NKE():
    url_Time_Series_NKE = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=NKE&apikey=B4UKNHORQ1AFHU68'
    r_NKE = requests.get(url_Time_Series_NKE)
    data_NKE = r_NKE.content
    data_json_NKE = json.loads(data_NKE)
    data_clean_NKE = data_json_NKE["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_NKE = [list_ticker[20], list_beta[20], list_employees[20], list_exchange[20], list_name[20],
                           list_52_high[20], list_52_low[20], list_description[20], list_volume[20],
                           list_outstanding[20], list_industry[20], list_headquarters[20], list_market_cap[20],
                           list_1_year_target[20], list_year_incorporated[20], list_stock_price[20]]
    list_CAPE_NKE = list(df_CAPE["NKE"])
    list_EXC_NKE =  list(df_EXC["NKE"])
    return render_template("Nike.html", data_API_NKE=data_clean_NKE, data_indicators_NKE=list_indicators_NKE, data_CAPE_NKE=list_CAPE_NKE, data_EXC_NKE=list_EXC_NKE)

@app.route("/PG", methods=["GET"])
@login_required
def PG():
    url_Time_Series_PG = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=PG&apikey=B4UKNHORQ1AFHU68'
    r_PG = requests.get(url_Time_Series_PG)
    data_PG = r_PG.content
    data_json_PG = json.loads(data_PG)
    data_clean_PG = data_json_PG["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_PG = [list_ticker[21], list_beta[21], list_employees[21], list_exchange[21], list_name[21],
                           list_52_high[21], list_52_low[21], list_description[21], list_volume[21],
                           list_outstanding[21], list_industry[21], list_headquarters[21], list_market_cap[21],
                           list_1_year_target[21], list_year_incorporated[21], list_stock_price[21]]
    list_CAPE_PG = list(df_CAPE["PG"])
    list_EXC_PG=  list(df_EXC["PG"])
    return render_template("Procter and Gamble.html", data_API_PG= data_clean_PG, data_indicators_PG=list_indicators_PG, data_CAPE_PG=list_CAPE_PG, data_EXC_PG=list_EXC_PG)

@app.route("/CRM", methods=["GET"])
@login_required
def CRM():
    url_Time_Series_CRM = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=CRM&apikey=B4UKNHORQ1AFHU68'
    r_CRM = requests.get(url_Time_Series_CRM)
    data_CRM = r_CRM.content
    data_json_CRM = json.loads(data_CRM)
    data_clean_CRM = data_json_CRM["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_CRM = [list_ticker[22], list_beta[22], list_employees[22], list_exchange[22], list_name[22],
                           list_52_high[22], list_52_low[22], list_description[22], list_volume[22],
                           list_outstanding[22], list_industry[22], list_headquarters[22], list_market_cap[22],
                           list_1_year_target[22], list_year_incorporated[22], list_stock_price[22]]
    return render_template("Salesforce.html", data_API_CRM=data_clean_CRM, data_indicators_CRM=list_indicators_CRM)

@app.route("/TRV", methods=["GET"])
@login_required
def TRV():
    url_Time_Series_TRV = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=TRV&apikey=B4UKNHORQ1AFHU68'
    r_TRV = requests.get(url_Time_Series_TRV)
    data_TRV = r_TRV.content
    data_json_TRV = json.loads(data_TRV)
    data_clean_TRV = data_json_TRV["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_TRV = [list_ticker[23], list_beta[23], list_employees[23], list_exchange[23], list_name[23],
                           list_52_high[23], list_52_low[23], list_description[23], list_volume[23],
                           list_outstanding[23], list_industry[23], list_headquarters[23], list_market_cap[23],
                           list_1_year_target[23], list_year_incorporated[23], list_stock_price[23]]
    list_CAPE_TRV = list(df_CAPE["TRV"])
    list_EXC_TRV =  list(df_EXC["TRV"])
    return render_template("Travelers.html", data_API_TRV=data_clean_TRV, data_indicators_TRV=list_indicators_TRV, data_CAPE_TRV=list_CAPE_TRV, data_EXC_TRV=list_EXC_TRV)

@app.route("/UNH", methods=["GET"])
@login_required
def UNH():
    url_Time_Series_UNH = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=UNH&apikey=B4UKNHORQ1AFHU68'
    r_UNH = requests.get(url_Time_Series_UNH)
    data_UNH = r_UNH.content
    data_json_UNH = json.loads(data_UNH)
    data_clean_UNH = data_json_UNH["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_UNH = [list_ticker[24], list_beta[24], list_employees[24], list_exchange[24], list_name[24],
                           list_52_high[24], list_52_low[24], list_description[24], list_volume[24],
                           list_outstanding[24], list_industry[24], list_headquarters[24], list_market_cap[24],
                           list_1_year_target[24], list_year_incorporated[24], list_stock_price[24]]
    list_CAPE_UNH = list(df_CAPE["UNH"])
    list_EXC_UNH =  list(df_EXC["UNH"])
    return render_template("United Health.html", data_API_UNH=data_clean_UNH, data_indicators_UNH=list_indicators_UNH, data_CAPE_UNH=list_CAPE_UNH, data_EXC_UNH=list_EXC_UNH)

@app.route("/VZ", methods=["GET"])
@login_required
def VZ():
    url_Time_Series_VZ = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=VZ&apikey=B4UKNHORQ1AFHU68'
    r_VZ = requests.get(url_Time_Series_VZ)
    data_VZ = r_VZ.content
    data_json_VZ = json.loads(data_VZ)
    data_clean_VZ = data_json_VZ["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_VZ = [list_ticker[25], list_beta[25], list_employees[25], list_exchange[25], list_name[25],
                           list_52_high[25], list_52_low[25], list_description[25], list_volume[25],
                           list_outstanding[25], list_industry[25], list_headquarters[25], list_market_cap[25],
                           list_1_year_target[25], list_year_incorporated[25], list_stock_price[25]]
    list_CAPE_VZ = list(df_CAPE["VZ"])
    list_EXC_VZ =  list(df_EXC["VZ"])
    return render_template("Verizon.html", data_API_VZ=data_clean_VZ, data_indicators_VZ=list_indicators_VZ, data_CAPE_VZ=list_CAPE_VZ, data_EXC_VZ=list_EXC_VZ)

@app.route("/V", methods=["GET"])
@login_required
def V():
    url_Time_Series_V = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=V&apikey=B4UKNHORQ1AFHU68'
    r_V = requests.get(url_Time_Series_V)
    data_V = r_V.content
    data_json_V = json.loads(data_V)
    data_clean_V = data_json_V["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_V = [list_ticker[26], list_beta[26], list_employees[26], list_exchange[26], list_name[26],
                           list_52_high[26], list_52_low[26], list_description[26], list_volume[26],
                           list_outstanding[26], list_industry[26], list_headquarters[26], list_market_cap[26],
                           list_1_year_target[26], list_year_incorporated[26], list_stock_price[26]]
    return render_template("Visa.html", data_API_V=data_clean_V, data_indicators_V=list_indicators_V)

@app.route("/WBA", methods=["GET"])
@login_required
def WBA():
    url_Time_Series_WBA = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=WBA&apikey=B4UKNHORQ1AFHU68'
    r_WBA = requests.get(url_Time_Series_WBA)
    data_WBA = r_WBA.content
    data_json_WBA = json.loads(data_WBA)
    data_clean_WBA = data_json_WBA["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_WBA = [list_ticker[27], list_beta[27], list_employees[27], list_exchange[27], list_name[27],
                           list_52_high[27], list_52_low[27], list_description[27], list_volume[27],
                           list_outstanding[27], list_industry[27], list_headquarters[27], list_market_cap[27],
                           list_1_year_target[27], list_year_incorporated[27], list_stock_price[27]]
    list_CAPE_WBA = list(df_CAPE["WBA"])
    list_EXC_WBA =  list(df_EXC["WBA"])
    return render_template("Walgreens Boots Alliance.html", data_API_WBA=data_clean_WBA, data_indicators_WBA=list_indicators_WBA, data_CAPE_WBA=list_CAPE_WBA, data_EXC_WBA=list_EXC_WBA)

@app.route("/WMT", methods=["GET"])
@login_required
def WMT():
    url_Time_Series_WMT = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=WMT&apikey=B4UKNHORQ1AFHU68'
    r_WMT = requests.get(url_Time_Series_WMT)
    data_WMT = r_WMT.content
    data_json_WMT = json.loads(data_WMT)
    data_clean_WMT = data_json_WMT["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_WMT = [list_ticker[28], list_beta[28], list_employees[28], list_exchange[28], list_name[28],
                           list_52_high[28], list_52_low[28], list_description[28], list_volume[28],
                           list_outstanding[28], list_industry[28], list_headquarters[28], list_market_cap[28],
                           list_1_year_target[28], list_year_incorporated[28], list_stock_price[28]]
    list_CAPE_WMT = list(df_CAPE["WMT"])
    list_EXC_WMT = list(df_EXC["WMT"])
    return render_template("Walmart.html", data_API_WMT=data_clean_WMT, data_indicators_WMT=list_indicators_WMT, data_CAPE_WMT=list_CAPE_WMT, data_EXC_WMT=list_EXC_WMT)

@app.route("/DIS", methods=["GET"])
@login_required
def DIS():
    url_Time_Series_DIS = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=DIS&apikey=B4UKNHORQ1AFHU68'
    r_DIS = requests.get(url_Time_Series_DIS)
    data_DIS = r_DIS.content
    data_json_DIS = json.loads(data_DIS)
    data_clean_DIS = data_json_DIS["Time Series (Daily)"][str(date_yesterday)]["4. close"]
    list_indicators_DIS = [list_ticker[29], list_beta[29], list_employees[29], list_exchange[29], list_name[29],
                           list_52_high[29], list_52_low[29], list_description[29], list_volume[29],
                           list_outstanding[29], list_industry[29], list_headquarters[29], list_market_cap[29],
                           list_1_year_target[29], list_year_incorporated[29], list_stock_price[29]]
    list_CAPE_DIS = list(df_CAPE["DIS"])
    list_EXC_DIS = list(df_EXC["DIS"])
    return render_template("Walt Disney.html", data_API_DIS=data_clean_DIS, data_indicators_DIS=list_indicators_DIS, data_CAPE_DIS=list_CAPE_DIS, data_EXC_DIS=list_EXC_DIS)

# Initialize the Flask APP with app.run

if __name__ == '__main__':
    app.run()
