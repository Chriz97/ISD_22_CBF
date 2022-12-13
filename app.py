import requests
import json
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_first_request
def create_tables():
     db.create_all()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=True, unique=True)
    password = db.Column(db.String(80), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    date_of_birth = StringField(validators=[InputRequired()], render_kw={"placeholder": "Date of birth"})

    submit = SubmitField('Sign up now')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

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


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('register.html', form=form)


@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template("main.html")

@app.route("/MMM", methods=["GET"])
def MMM():

    return render_template("3M.html")

@app.route("/AXP", methods=["GET"])
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

if __name__ == '__main__':
    app.run()
