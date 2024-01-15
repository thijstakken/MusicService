from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# this is the database object
db = SQLAlchemy()
    
# this is the application object
app = Flask(__name__)

from webapp import routes