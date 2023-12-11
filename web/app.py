from __future__ import unicode_literals
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
    new_music = Music(title=title, url=url, complete=False)
    db.session.add(new_music)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:music_id>")
def update(music_id):
    music = Music.query.filter_by(id=music_id).first()
    music.complete = not music.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:music_id>")
def delete(music_id):
    music = Music.query.filter_by(id=music_id).first()
    db.session.delete(music)
    db.session.commit()
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
        
        WebDAV_URL = request.form.get("WebDAV_URL")
        WebDAV_Directory = request.form.get("WebDAV_Directory")
        WebDAV_Username = request.form.get("WebDAV_Username")
        WebDAV_Password = request.form.get("WebDAV_Password")
        WebDAVSettings = WebDAV(WebDAV_URL=WebDAV_URL, WebDAV_Directory=WebDAV_Directory, WebDAV_Username=WebDAV_Username, WebDAV_Password=WebDAV_Password)
        db.session.add(WebDAVSettings)
        db.session.commit()
        return redirect(url_for("settings"))
    
    # if query is not "None" then some settings have been configured already and we just want to change those records
    else:
        settings = WebDAV.query.filter_by(id=1).first()
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
        # add song
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

def downloadmusic(music_id):
    # get the URL for the playlist/song
    for (url, ) in db.session.query(Music.url).filter_by(id=music_id):
        print(url)

        print("")
        print("Downloading playlist...", music_id)

        downloadPlaylists(ydl_opts, url)

        for (complete, ) in db.session.query(Music.complete).filter_by(id=music_id):
            if complete == True:

                print("sync is ON")
                print("Going to upload the music to the cloud account")
                print(complete)


                # start uploading the music
                ##########################
                
                # THIS IS TEMPORARY
                localDirectory = 'music'
                print("")
                print('Creating cloud folder structure based on local directories...')
                create_folders(localDirectory)

                print("")
                print('Uploading music into the cloud folders...')
                upload_music(remoteDirectory)

                #print("Clearing local MP3 files since they are no longer needed...")
                #clear_local_music_folder()

            else:
                print("sync is OFF")
                print("NOT uploading songs because sync is turned off")
                print(complete)


@app.route("/download/<int:music_id>")
def download(music_id):

    # call download function and pass the music_id we want to download to it
    downloadmusic(music_id)

    return redirect(url_for("home"))

# let users configure their interval value on a per playlist/song basis
@app.route("/interval/<int:music_id>")
def interval(music_id):
    
    # at the moment it accepts everything. but it should only allow integers as input.
    # close this down somewhere so only integers are allowed through this method.
    interval = request.args.get('interval', None) # None is the default value
    
    music = Music.query.filter_by(id=music_id).first()
    music.interval = interval
    db.session.commit()
    print(interval)
    print(interval)
    print(interval)
    print(interval)
    print(interval)

    return redirect(url_for("home"))

# function which will keep an interval time for each playlist/song in the background
# this will be used to check if the playlist/song needs to be downloaded again
# if the interval time has passed, then the playlist/song will be downloaded again
# this will be used to keep the music up to date
def scheduleJobs():
    # get all the playlists/songs
    music_list = Music.query.all()

    # iterate over the playlists/songs
    for music in music_list:
        # get the interval value for each playlist/song
        interval = music.interval

        # https://github.com/dbader/schedule
        # https://schedule.readthedocs.io/en/stable/
        schedule.every(interval).minutes.do(downloadmusic,music.id)
        print("Interval set for:", music.title, interval, "minutes")

    print('here are all jobs', schedule.get_jobs())
    

def run_schedule(app_context):
    app_context.push()
    # run the schedule in the background
    while True:
        schedule.run_pending()
        time.sleep(1)

# YT-DLP logging
class MyLogger(object):
    def debug(self, msg):   # print debug
        print(msg)
        #pass

    def warning(self, msg): # print warnings
        print(msg)
        #pass

    def error(self, msg):   # always print errors
        print(msg)

# shows progress of the downloads
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

# Configure YouTube DL options
ydl_opts = {
    'writethumbnail': True,
    'no_write_playlist_metafiles': True,                            # do not save playlist data, like playlist .png
    'format': 'bestaudio[asr<=44100]/best[asr<=44100]/bestaudio',   # using asr 44100 as max, this mitigates exotic compatibility issues with certain mediaplayers, and allow bestaudio as a fallback for direct mp3s
    'postprocessors': [{    
        'key': 'FFmpegExtractAudio',                                # use FFMPEG and only save audio
        'preferredcodec': 'mp3',                                    # convert to MP3 format
        #'preferredquality': '192',                                 # with not specifying a preffered quality, the original bitrate will be used, therefore skipping one unnecessary conversion and keeping more quality
        },
    {'key': 'EmbedThumbnail',},                                     # embed the Youtube thumbnail with the MP3 as coverart.
    ],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': './music/%(playlist)s/%(title)s-%(id)s.%(ext)s',     # save music to the /music folder. and it's corrosponding folder which will be named after the playlist name
    'simulate': False,                                              # to dry test the YT-DL, if set to True, it will skip the downloading. Can be True/False
    'cachedir': False,                                              # turn off caching, this should mitigate 403 errors which are commonly seen when downloading from Youtube
    'download_archive': '../download_archive/downloaded',           # this will update the downloads file which serves as a database/archive for which songs have already been downloaded, so it don't downloads them again
    'nocheckcertificates': True,                                    # mitigates YT-DL bug where it wrongly examins the server certificate, so therefore, ignore invalid certificates for now, to mitigate this bug
}

# this was ment to recieve a list of strings, but now I put in 1 URL at a time. change needed for stability? could be simplerer now
# downloads the playlist/song with the specified options in ydl_opts
def downloadPlaylists(ydl_opts, lines):
    with YoutubeDL(ydl_opts) as ydl:
                ydl.download(lines)

# creates directories in the cloud based on the local directory structure
def create_folders(localDirectory):
    
    # for every local directory create a directory at the users remote cloud directory
    for localDirectory, dirs, files in os.walk(localDirectory):
        for subdir in dirs:
            
            # construct URl to make calls to
            print(os.path.join(localDirectory, subdir))

            # remove first / from the string to correct the formatting of the URL
            formatRemoteDir = remoteDirectory[1:]

            fullurl = url + formatRemoteDir + "/" + subdir

            # first check if the folder already exists
            existCheck = requests.get(fullurl, auth=(username, password))

            # if the folder does not yet exist (everything except 200 code) then create that directory
            if not existCheck.status_code == 200:
                
            # create directory and do error handling, when an error occurs, it will print the error information and stop the script from running
                try:
                    r = requests.request('MKCOL', fullurl, auth=(username, password))
                    print("")
                    print(r.text)
                    print("Created directory: ")
                    print(r.url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as erra:           # handle 4xx and 5xx HTTP errors
                    print("HTTP Error: ",erra)
                    raise SystemExit(erra)  
                except requests.exceptions.ConnectionError as errb:     # handle network problems, DNS, refused connections
                    print("Error Connecting: ",errb)
                    raise SystemExit(errb)
                except requests.exceptions.Timeout as errc:             # handle requests that timed out
                    print("Timeout Error: ",errc)
                    raise SystemExit(errc)
                except requests.exceptions.TooManyRedirects as eerd:    # handle too many redirects, when a webserver is wrongly configured
                    print("Too many redirects, the website redirected you too many times: ",eerd)
                    raise SystemExit(eerd)
                except requests.exceptions.RequestException as erre:    # handle all other exceptions which are not handled exclicitly
                    print("Something went wrong: ",erre)
                    raise SystemExit(erre)
            
            # if directory exists print message that is exists and it will skip it
            else:
                print("Directory already exists, skipping: " + fullurl)

    print("Finished creating directories")

# after the neccessary directories have been created we can start to put the music into the folders
# iterates over files and uploads them to the corresponding directory in the cloud
def upload_music(remoteDirectory):
    # THIS IS TEMPORARY
    localDirectory = 'music'
    for root, dirs, files in os.walk(localDirectory):
        for filename in files:
            
            # get full path to the file (example: 'music/example playlist/DEAF KEV - Invincible [NCS Release].mp3')
            path = os.path.join(root, filename)
            
            # removes the first 6 characters "music/" from the path, beacause that piece of the path is not needed and should be ignored
            reduced_path = path[6:]

            # get the folder name in which the file is located (example: 'example playlist')
            subfoldername = os.path.basename(os.path.dirname(reduced_path))
            
            # remove first / from the string to correct the formatting of the URL
            formatRemoteDir = remoteDirectory[1:]

            # construct the full url so we can PUT the file there
            fullurl = url + formatRemoteDir + "/" + subfoldername + "/" + filename
            
            # first check if the folder already exists
            existCheck = requests.get(fullurl, auth=(username, password))
            
            # if the file does not yet exist (everything except 200 code) then create that file
            if not existCheck.status_code == 200:
            # error handling, when an error occurs, it will print the error and stop the script from running
                try:

                    # configure header, set content-type as mpeg and charset to utf-8 to make sure that filenames with special characters are not being misinterpreted
                    headers = {'Content-Type': 'audio/mpeg; charset=utf-8', }
                    
                    # make the put request, this uploads the file
                    r = requests.put(fullurl, data=open(path, 'rb'), headers=headers, auth=(username, password))
                    print("")
                    print(r.text)
                    print("Uploading file: ")
                    print(r.url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as erra:           # handle 4xx and 5xx HTTP errors
                    print("HTTP Error: ",erra)
                    raise SystemExit(erra)  
                except requests.exceptions.ConnectionError as errb:     # handle network problems, DNS, refused connections
                    print("Error Connecting: ",errb)
                    raise SystemExit(errb)
                except requests.exceptions.Timeout as errc:             # handle requests that timed out
                    print("Timeout Error: ",errc)
                    raise SystemExit(errc)
                except requests.exceptions.TooManyRedirects as eerd:    # handle too many redirects, when a webserver is wrongly configured
                    print("Too many redirects, the website redirected you too many times: ",eerd)
                    raise SystemExit(eerd)
                except requests.exceptions.RequestException as erre:    # handle all other exceptions which are not handled exclicitly
                    print("Something went wrong: ",erre)
                    raise SystemExit(erre)
            
            # if file exists print message that is exists and it will skip it
            else:
                print("File already exists, skipping: " + fullurl)

            # in the event that the file either has been uploaded or already existed, we can delete the local copy
            print("Removing local file,", path, "no longer needed after upload")
            os.remove(path)

        # check if there are any directories left, if there are, we can delete them if they are empty
        # we want to remove unneeded files and dirs so they don't pile up until your storage runs out of space
        for directory in dirs:
            dirToDelete = os.path.join(root, directory)
            
            dirStatus = os.listdir(dirToDelete)

            if len(dirStatus) == 0:
                print("Empty DIRECTORY")
                print("Removing local directory,", dirToDelete, "no longer needed after upload")
                try:
                    os.rmdir(dirToDelete)
                    print("Done...")
                except OSError as error:
                    print(error)
                    print(dirToDelete)

            else:
                print("NOT EMPTY DIRECTORY")
                print("Cannot delete yet...")
            
    
    print("Finished uploading music files")


if __name__ == "__main__":

    # used for message flashing, look for "flash" to see where it's used
    app.secret_key = b'/\xed\xb4\x87$E\xf4O\xbb\x8fpb\xad\xc2\x88\x90!\x89\x18\xd0z\x15~Z'

    # had to add app.app otherwise would not work properly
    # this fixes the working outside of application context error
    # article with fix https://sentry.io/answers/working-outside-of-application-context/
    # why did it fix it, is it really the best solution, is it even needed? Or is my programming so bad, it can't work without this workaround?
    with app.app_context():
        db.create_all()

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
        scheduleJobs()
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