from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = './app/static/uploads' 

app.config['SECRET_KEY'] = "CAKBRF"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:password@localhost/wishlist"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_AUTH_ENDPOINT'] = 'Bearer'

db = SQLAlchemy(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views
