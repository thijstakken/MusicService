from __future__ import unicode_literals
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, Blueprint
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
from web import db
# from . import db

# import the downloadmusic function from the downloadMusic.py file
#from downloadMusic import downloadmusic
#from uploadMusic import uploadmusic
from web.downloadScheduler import scheduleJobs, deleteJobs, immediateJob, run_schedule


main = Blueprint('main', __name__)


@main.route("/")
def home():
    music_list = Music.query.all()
    return render_template("base.html", music_list=music_list)

@main.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    url = request.form.get("url")
    new_music = Music()
    new_music.title = title
    new_music.url = url
    new_music.monitored = False
    new_music.interval = 10
    db.session.add(new_music)
    db.session.commit()
    
    # at the moment, the schedule is always false upon creation. so this is not needed at the moment
    # this has already been used in the monitor function below this function.
    #if new_music.monitored is False:
        # schedule a job for the newly added playlist/song with the corrosponding interval value
    #    scheduleJobs(music_id, title, interval)
    return redirect(url_for("home"))

@main.route("/monitor/<int:music_id>")
def monitor(music_id):
    music = Music.query.filter_by(id=music_id).first()
    # turned below rule off because during startup the settings are already set.
    #settings = WebDAV.query.filter_by(id=1).first()
    if music is not None:
        music.monitored = not music.monitored
        db.session.commit()
        if music.monitored is True and settings is not None:
            print("monitor is ON")
            print("Going to schedule the music to be downloaded on repeat")
            print(music.monitored)
            # schedule a job for the newly added playlist/song with the corrosponding interval value
            scheduleJobs(music, settings)
        elif music.monitored is False:
            print("monitor is OFF")
            print("Going to delete the scheduled job")
            #print(music.monitored)
            # delete the scheduled job for the deleted playlist/song
            deleteJobs(music.id)
    return redirect(url_for("home"))

@main.route("/delete/<int:music_id>")
def delete(music_id):
    music = Music.query.filter_by(id=music_id).first()
    db.session.delete(music)
    db.session.commit()
    # delete the scheduled job for the deleted playlist/song
    deleteJobs(music_id)
    return redirect(url_for("home"))

@main.route("/download/<int:music_id>")
def download(music_id):
    # get the music object from the database
    music = Music.query.filter_by(id=music_id).first()
    # execute the download function to download one time
    if music is not None and settings is not None:
        immediateJob(music, settings)
    return redirect(url_for("home"))

# let users configure their interval value on a per playlist/song basis
@main.route("/interval/<int:music_id>")
def interval(music_id):
    
    # at the moment it accepts everything. but it should only allow integers as input.
    # close this down somewhere so only integers are allowed through this method.
    interval = request.args.get('interval', None) # None is the default value if no interval is specified
    
    music = Music.query.filter_by(id=music_id).first()
    settings = WebDAV.query.filter_by(id=1).first()
    if music:
        music.interval = interval
        db.session.commit()
        #print(interval)
        
        # if the monitor is on, then reschedule the job with the new interval value
        if music.monitored is True:
            print("Going to reschedule the music to be downloaded on repeat")
            # delete the scheduled job for the deleted playlist/song
            deleteJobs(music_id)
            # schedule a job for the newly added playlist/song with the corrosponding interval value
            scheduleJobs(music, settings)

    return redirect(url_for("home"))

# this function can get the time left before the playlist will be downloaded again
@main.route("/intervalstatus/<int:music_id>")
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



### WEBDAV FUNCTIONS SETTINGS ###

@main.route("/settings")
def settings():
    # get settings
    WebDAVconfig = WebDAV.query.all()

    # get songs archive
    with open(r"../download_archive/downloaded", 'r') as songs:
        songs = songs.readlines()
        # add song ID's so they are easy to delete/correlate
        songs = list(enumerate(songs))
    
    return render_template("settings.html", WebDAVconfig=WebDAVconfig, songs=songs)

@main.route("/settings/save", methods=["POST"])
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

### END WEBDAV FUNCTIONS SETTINGS ###



### ARCHIVE FUNCTIONS ###

@main.route("/archiveaddsong", methods=["POST"])
def archiveaddsong():
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

@main.route("/archivedeletesong/<int:song_id>")
def archivedeletesong(song_id):
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

@main.route('/archivedownload') # GET request
# based on flask.send_file method: https://flask.palletsprojects.com/en/2.3.x/api/#flask.send_file
def archivedownload():
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
@main.route("/archiveupload", methods=["POST"])
def archiveupload():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
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
  
### END ARCHIVE FUNCTIONS ###
        


#if __name__ == "__main__":

    # let's dance: "In 5, 6, 7, 8!"
#    main.run(debug=True, port=5678)