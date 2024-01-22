from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
    
# this is the application object
app = Flask(__name__)

# gets config from config.py
app.config.from_object(Config)

# this is the database object
db = SQLAlchemy(app)

# this is the migration engine
migrate = Migrate(app, db)

# gets all the routes for the web application
from webapp import routes, models