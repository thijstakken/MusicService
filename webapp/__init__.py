from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis
import rq


# this is the database object
db = SQLAlchemy()
# this is the migration engine
migrate = Migrate()
# this is the login manager
login = LoginManager()
login.login_view = 'auth.login'
#login.login_message = _l('Please log in to access this page.')

def create_app(config_class=Config):
    # this is the application object
    app = Flask(__name__)
    # gets config from config.py
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from webapp.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from webapp.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from webapp.main import bp as main_bp
    app.register_blueprint(main_bp)

    #from webapp.music import bp as music_bp
    #app.register_blueprint(music_bp)

    from webapp.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')


    #if not app.debug and not app.testing:
    # add testing/debug later


    return app


    # # start running the run_schedule function in the background
    # # get all the playlists/songs
    # music_list = Music.query.all()
    # settings = WebDAV.query.filter_by(id=1).first()
    # # iterate over the playlists/songs
    # for music in music_list:
    #     # make sure the playlist/song is set to be monitored
    #     if music.monitored is True and settings is not None:
    # # get the interval value for each playlist/song
    #         scheduleJobs(music, settings)
    # print('here are all jobs', schedule.get_jobs())

    # #interval_check()

    # # start the schedule in the background as a seperated thread from the main thread
    # # this is needed to let the scheduler run in the background, while the main thread is used for the webserver
    # t = threading.Thread(target=run_schedule, args=(app.app_context(),), daemon=True)
    # t.start()


    # setting general variables
    # 'music' always use music as local, this can't be changed at the moment, due to some hardcoding
    # make the localDirectory global so it can be used in other functions
    #global localDirectory
"""
The line of code you've shared is in Python and it's making use of the `global` keyword.
The `global` keyword in Python is used to indicate that a variable is a global variable, meaning it can be accessed from anywhere in the code, not just in the scope where it was declared. 
In this case, `localDirectory` is being declared as a global variable. This means that `localDirectory` can be used, modified, or re-assigned in any function within this Python script, not just the function where it's declared.
However, it's important to note that using global variables can make code harder to understand and debug, because any part of the code can change the value of the variable. It's generally recommended to use local variables where possible, and pass data between functions using arguments and return values.
"""
    #localDirectory = 'music'

# # check if file ../download_archive/downloaded exists
# archive_directory = '../download_archive/'
# archive_file = 'downloaded'
# download_archive = os.path.join(archive_directory, archive_file)

# if os.path.isfile(download_archive) == False:
#     # tries to create the archive directory and file

#     print("Download archive does not exist")

#     # tries to create archive directory
#     try:
#         print("Creating directory...")
#         output = os.mkdir(archive_directory)
#         print("Directory '% s' created" % archive_directory)
#     except OSError as error:
#         print(error)

#     # tries to create archive file
#     try:
#         print("Creating file...")
#         open(download_archive, 'x')
#         print("File '% s' created" % download_archive)
#     except OSError as error:
#         print(error)

#     else:
#         print("Download archive exists, nothing to do...")



# gets all the routes for the web application
#from webapp import routes, models

from webapp import models


# print Python version for informational purposes
#print("Python version: "+ sys.version)

# welcome message
print("Starting MusicService")
version = '2024.3'
print("Version:", version)

# blueprint for auth routes in our app
# from .auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
#from .routes import main as main_blueprint
#app.register_blueprint(main_blueprint)