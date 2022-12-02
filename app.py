from flask import Flask, render_template, url_for, request, redirect
import requests
import json

app = Flask(__name__, static_url_path='/static')


@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template("main.html")


@app.route("/IBM", methods=["GET"])
def IBM():
    url_Time_Series_DBK = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=M9YDWDBER8VD0BTV'
    r_DBK = requests.get(url_Time_Series_DBK)
    data = r_DBK.content
    data_json1 = json.loads(data)
    data_clean1 = data_json1["Time Series (Daily)"]["2022-11-03"]["4. close"]
    return render_template("IBM.html", data=data_clean1)

@app.route("/TEST")
def Test():
    return render_template("Table.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    logged_in = False
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            logged_in = True
        else:
            return redirect(url_for('hello_world'))
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run()
