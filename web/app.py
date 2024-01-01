from __future__ import unicode_literals
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from re import L
from yt_dlp import YoutubeDL
import shutil
import requests
import os
import os.path
import time
import sys
from pathlib import Path
import schedule
import threading

# import the downloadmusic function from the downloadMusic.py file
from downloadMusic import downloadmusic
from uploadMusic import uploadmusic
from downloadScheduler import scheduleJobs, scheduleNewJobs, deleteJobs, run_schedule

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    interval = db.Column(db.Integer)

class WebDAV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    WebDAV_URL = db.Column(db.String(250))
    WebDAV_Directory = db.Column(db.String(250))
    WebDAV_Username = db.Column(db.String(30))
    WebDAV_Password = db.Column(db.String(100))

@app.route("/")
def home():
    music_list = Music.query.all()
    return render_template("base.html", music_list=music_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    url = request.form.get("url")
    new_music = Music()
    new_music.title = title
    new_music.url = url
    new_music.complete = False
    new_music.interval = 10
    db.session.add(new_music)
    db.session.commit()

    # get the id of the newly added playlist/song
    music_id = new_music.id

    # get the interval value for the newly added playlist/song
    interval = new_music.interval

    # get the title of the newly added playlist/song
    title = new_music.title

    # schedule a job for the newly added playlist/song with the corrosponding interval value
    scheduleNewJobs(music_id, title, interval)

    return redirect(url_for("home"))

@app.route("/update/<int:music_id>")
def update(music_id):
    music = Music.query.filter_by(id=music_id).first()
    if music is not None:
        music.complete = not music.complete
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:music_id>")
def delete(music_id):
    music = Music.query.filter_by(id=music_id).first()
    db.session.delete(music)
    db.session.commit()
    # delete the scheduled job for the deleted playlist/song
    deleteJobs(music_id)
    return redirect(url_for("home"))

@app.route("/settings")
def settings():
    # get settings
    WebDAVconfig = WebDAV.query.all()

    # get songs archive
    with open(r"../download_archive/downloaded", 'r') as songs:
        songs = songs.readlines()
        # add song ID's so they are easy to delete/correlate
        songs = list(enumerate(songs))
    
    return render_template("settings.html", WebDAVconfig=WebDAVconfig, songs=songs)

@app.route("/settings/save", methods=["POST"])
def settingsSave():
    
    # if the settings are not set, the row will be empty, so "None"
    # then create the row and save the settings
    if WebDAV.query.filter_by(id=1).first() is None:
        
        WebDAVSettings = WebDAV()
        WebDAVSettings.WebDAV_URL = request.form.get("WebDAV_URL")
        WebDAVSettings.WebDAV_Directory = request.form.get("WebDAV_Directory")
        WebDAVSettings.WebDAV_Username = request.form.get("WebDAV_Username")
        WebDAVSettings.WebDAV_Password = request.form.get("WebDAV_Password")
        db.session.add(WebDAVSettings)
        db.session.commit()
        return redirect(url_for("settings"))
    
    # if query is not "None" then some settings have been configured already and we just want to change those records
    else:
        settings = WebDAV.query.filter_by(id=1).first()
        if settings is not None:
            settings.WebDAV_URL = request.form.get("WebDAV_URL")
            settings.WebDAV_Directory = request.form.get("WebDAV_Directory")
            settings.WebDAV_Username = request.form.get("WebDAV_Username")
            settings.WebDAV_Password = request.form.get("WebDAV_Password")
            db.session.commit()
        return redirect(url_for("settings"))

@app.route("/deletesong/<int:song_id>")
def deletesong(song_id):
    # get songs archive
    with open(r"../download_archive/downloaded", 'r') as fileop:
        songs = fileop.readlines()

    # delete/clear the correct row
    with open(r"../download_archive/downloaded", 'w') as fileop:
        for number, line in enumerate(songs):
        # delete/clear the song_id line
            if number not in [song_id]:
                fileop.write(line)    

    return redirect(url_for("settings"))

@app.route("/addsong", methods=["POST"])
def addsong():
    song = request.form.get("song")

    # get archive for analysis
    with open("../download_archive/downloaded") as file:
        text = file.read()

    # add new song to archive
    with open(r"../download_archive/downloaded", 'a') as archive:
        # check if a newline already exists
        if not text.endswith('\n'):
            # if it does not end with a newline, then add it
            archive.write('\n')
        # add song if it is not None
        if song is not None:
            archive.write(song)
    return redirect(url_for("settings"))

@app.route('/downloadarchive') # GET request
# based on flask.send_file method: https://flask.palletsprojects.com/en/2.3.x/api/#flask.send_file
def downloadarchive():
    return send_file(
        '../download_archive/downloaded',
        mimetype='text/plain',
        download_name='download_archive.txt',
        as_attachment=True
    )

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# used flask uploading files guide https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
@app.route('/uploadarchive', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # read the contents
            archive_content = file.read()
            # decode the multipart form-data (bytes) into str
            archive_content = archive_content.decode()

            # split each line, and put each line into lines_list
            lines_list = archive_content.split('\n')

            # read existing archive
            with open("../download_archive/downloaded") as archive_data:
                text = archive_data.read()

            # add new songs to archive
            with open(r"../download_archive/downloaded", 'a') as archive:
                
                # check if newline already exists, always start with a newline
                if not text.endswith('\n'):
                        # if it does not end with a newline, then add it
                        archive.write('\n')
                        #print("newline added")

                # for every line we want to write it to the archive file
                for line in lines_list:
                    #print(line, 'was added')
                    # write the line to the arhive
                    archive.write(line)
                    # always add a newline after a new addition, to get ready for the next one
                    archive.write('\n')
                    # because of this, after the last item, a newline will also be added, as a result of which you will always have a empty row on the bottom of the archive
                    # which does look a bit weird... look into later

            return redirect(url_for('settings'))

@app.route("/download/<int:music_id>")
def download(music_id):

    # get the URL for the playlist/song
    for (url, ) in db.session.query(Music.url).filter_by(id=music_id):
        print(url)
        # call download function and pass the music_id we want to download to it
        downloadmusic(music_id, url)

    # get WebDAV settings
    settings = WebDAV.query.filter_by(id=1).first()
    if settings is not None:
        url = settings.WebDAV_URL
        remoteDirectory = settings.WebDAV_Directory
        username = settings.WebDAV_Username
        password = settings.WebDAV_Password
    
        # call upload function to upload the music to the cloud
        uploadmusic(url, username, password, remoteDirectory)

    return redirect(url_for("home"))

# let users configure their interval value on a per playlist/song basis
@app.route("/interval/<int:music_id>")
def interval(music_id):
    
    # at the moment it accepts everything. but it should only allow integers as input.
    # close this down somewhere so only integers are allowed through this method.
    interval = request.args.get('interval', None) # None is the default value if no interval is specified
    
    music = Music.query.filter_by(id=music_id).first()
    music.interval = interval
    db.session.commit()
    print(interval)
    print(interval)
    print(interval)
    print(interval)
    print(interval)

    return redirect(url_for("home"))


# this function can get the time left before the playlist will be downloaded again
@app.route("/intervalstatus/<int:music_id>")
def intervalStatus(music_id):
    
    time_of_next_run = schedule.next_run(music_id)
    # get current time
    time_now = datetime.now()
    
    if time_of_next_run is not None:
        # calculate time left before next run
        time_left = time_of_next_run - time_now
        print("Time left before next run:", time_left)
        time_left = time_left.seconds
    else:
        time_left = 0
    
    # return the time left before the next run
    return str(time_left)


if __name__ == "__main__":

    # used for message flashing, look for "flash" to see where it's used
    app.secret_key = b'/\xed\xb4\x87$E\xf4O\xbb\x8fpb\xad\xc2\x88\x90!\x89\x18\xd0z\x15~Z'

    # had to add app.app otherwise would not work properly
    # this fixes the working outside of application context error
    # article with fix https://sentry.io/answers/working-outside-of-application-context/
    # why did it fix it, is it really the best solution, is it even needed? Or is my programming so bad, it can't work without this workaround?
    with app.app_context():
        db.create_all()

        # delete id 6 from the database, this is a leftover from testing
        #delete(6)

        if WebDAV.query.filter_by(id=1).first() is not None:
            settings = WebDAV.query.filter_by(id=1).first()
            url = settings.WebDAV_URL
            remoteDirectory = settings.WebDAV_Directory
            username = settings.WebDAV_Username
            password = settings.WebDAV_Password
        else:
        # sent user to settings page???
            pass

        # start running the run_schedule function in the background
        scheduleJobs(Music)
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

    # let's dance: "In 5, 6, 7, 8!"
    app.run(debug=True, port=5678)