# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'/\xed\xb4\x87$E\xf4O\xbb\x8fpb\xad\xc2\x88\x90!\x89\x18\xd0z\x15~Z'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    monitored = db.Column(db.Boolean)
    interval = db.Column(db.Integer)

class WebDAV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    WebDAV_URL = db.Column(db.String(250))
    WebDAV_Directory = db.Column(db.String(250))
    WebDAV_Username = db.Column(db.String(30))
    WebDAV_Password = db.Column(db.String(100))

# initialize the database object
db.init_app(app)

# create the database
with app.app_context():
    db.create_all()


# blueprint for auth routes in our app
from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .routes import main as main_blueprint
app.register_blueprint(main_blueprint)


# temp placed here, should be moved to a better location later
#return app





# had to add app.app otherwise would not work properly
    # this fixes the working outside of application context error
    # article with fix https://sentry.io/answers/working-outside-of-application-context/
    # why did it fix it, is it really the best solution, is it even needed? Or is my programming so bad, it can't work without this workaround?
    
    
    #with app.app_context():
    #    db.create_all()



    # delete id 6 from the database, this is a leftover from testing
    #delete(6)

    #settings = WebDAV.query.filter_by(id=1).first()
    #if settings is not None:
    #    url = settings.WebDAV_URL
    #    remoteDirectory = settings.WebDAV_Directory
    #    username = settings.WebDAV_Username
    #    password = settings.WebDAV_Password
    #else:
    # sent user to settings page???
    #    pass



    # start running the run_schedule function in the background
    # get all the playlists/songs
    music_list = Music.query.all()
    settings = WebDAV.query.filter_by(id=1).first()
    # iterate over the playlists/songs
    for music in music_list:
        # make sure the playlist/song is set to be monitored
        if music.monitored is True and settings is not None:
    # get the interval value for each playlist/song
            scheduleJobs(music, settings)
    print('here are all jobs', schedule.get_jobs())

    #interval_check()

    # start the schedule in the background as a seperated thread from the main thread
    # this is needed to let the scheduler run in the background, while the main thread is used for the webserver
    t = threading.Thread(target=run_schedule, args=(app.app_context(),), daemon=True)
    t.start()

    # setting general variables
    # 'music' always use music as local, this can't be changed at the moment, due to some hardcoding
    # make the localDirectory global so it can be used in other functions
    global localDirectory
    """
    The line of code you've shared is in Python and it's making use of the `global` keyword.
    ```
    python
    global localDirectory
    ```
    The `global` keyword in Python is used to indicate that a variable is a global variable, meaning it can be accessed from anywhere in the code, not just in the scope where it was declared. 
    In this case, `localDirectory` is being declared as a global variable. This means that `localDirectory` can be used, modified, or re-assigned in any function within this Python script, not just the function where it's declared.
    However, it's important to note that using global variables can make code harder to understand and debug, because any part of the code can change the value of the variable. It's generally recommended to use local variables where possible, and pass data between functions using arguments and return values.
    """
    localDirectory = 'music'


    # check if file ../download_archive/downloaded exists
    archive_directory = '../download_archive/'
    archive_file = 'downloaded'
    download_archive = os.path.join(archive_directory, archive_file)

    if os.path.isfile(download_archive) == False:
        # tries to create the archive directory and file

        print("Download archive does not exist")

        # tries to create archive directory
        try:
            print("Creating directory...")
            output = os.mkdir(archive_directory)
            print("Directory '% s' created" % archive_directory)
        except OSError as error:
            print(error)

        # tries to create archive file
        try:
            print("Creating file...")
            open(download_archive, 'x')
            print("File '% s' created" % download_archive)
        except OSError as error:
            print(error)

        else:
            print("Download archive exists, nothing to do...")


    # print Python version for informational purposes
    print("Python version: "+ sys.version)

    # welcome message
    print("Starting MusicService")
    version = '2023.9'
    print("Version:", version)