from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models.models import db, User
import os

load_dotenv()

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('AWS_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Set the secret key for secure sessions
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRETKEY')


db.init_app(app)

migrate = Migrate(app, db)

from routes.home_routes import *

if __name__ == '__main__':
    app.run(debug=True)