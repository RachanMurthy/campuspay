from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from eth_connect import connect_to_ethereum
from datetime import timedelta

w3 = connect_to_ethereum()
if connect_to_ethereum() == -1:
    raise Exception("CONNECTION TO BLOCKCHAIN FAILED")

app = Flask(__name__)

app.config['SECRET_KEY'] ='b1946ac92492d2347c6235b4d2611184'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=30)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from . import routes 