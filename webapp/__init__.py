from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis
import rq
from flask_moment import Moment
import threading
import schedule
import time
import os

# this is the database object
db = SQLAlchemy()
# this is the migration engine
migrate = Migrate()
# this is the login manager
login = LoginManager()
login.login_view = 'auth.login'
#login.login_message = _l('Please log in to access this page.')
moment = Moment()

def create_app(config_class=Config, baseconfig=False):
    # this is the application object
    app = Flask(__name__)
    # gets config from config.py
    app.config.from_object(config_class)

    db.init_app(app)

    if not baseconfig:
        migrate.init_app(app, db)
        login.init_app(app)
        moment.init_app(app)

        app.redis = Redis.from_url(app.config['REDIS_URL'])
        app.task_queue = rq.Queue('music-tasks', connection=app.redis)

        from webapp.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from webapp.main import bp as main_bp
        app.register_blueprint(main_bp)

        #from webapp.music import bp as music_bp
        #app.register_blueprint(music_bp)

        from webapp.settings import bp as settings_bp
        app.register_blueprint(settings_bp)


        #if not app.debug and not app.testing:
        # add testing/debug later


        # this functions runs in a seperate thread to monitor scheduled jobs and run them when needed
        def run_schedule(app_context):
            with app_context:  # Use the context manager to ensure proper push and pop
                try:
                    # run the schedule in the background
                    while True:
                        schedule.run_pending()
                        time.sleep(1)
                except Exception as e:
                    # Log the exception or handle it as needed
                    print(f"Error in scheduled task: {e}")
                finally:
                    # Any necessary cleanup can go here
                    pass
        
        if os.environ.get('FLASK_DB_UPGRADE') != '1':
            # start the schedule in the background as a separated thread from the main thread
            # this is needed to let the scheduler run in the background, while the main thread is used for the webserver
            t = threading.Thread(target=run_schedule, args=(app.app_context(),), daemon=True)
            t.start()


        # this function will start the scheduler for all the scheduled jobs
        def schedulerboot():
            try:
                # call the function to start the scheduler
                from webapp.main.routes import schedulerbootup
                schedulerbootup()
            except Exception as e:
                # Log the exception or handle it as needed
                print(f"Error initializing scheduler: {e}")
        
        if os.environ.get('FLASK_DB_UPGRADE') != '1':
            # the app_context pushes and pops the context automatically
            with app.app_context():
                schedulerboot()

    # always register the error handler
    from webapp.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app

from webapp import models


# print Python version for informational purposes
#print("Python version: "+ sys.version)

# welcome message
print("Starting MusicService")
version = '2024.7'
print("Version:", version)