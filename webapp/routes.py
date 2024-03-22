from __future__ import unicode_literals
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from webapp import db
from webapp.models import User
from webapp.models import Music
from webapp.models import CloudStorage
from webapp.models import WebDavStorage
from webapp.forms import RegistrationForm
from urllib.parse import urlsplit

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
#from downloadMusic import downloadmusic
#from uploadMusic import uploadmusic
from webapp.downloadScheduler import scheduleJobs, deleteJobs, immediateJob, run_schedule

from webapp import app

from webapp.forms import LoginForm
from webapp.forms import MusicForm
from webapp.forms import WebDAV

from sqlalchemy import select


# blueprint will be activeated later
#main = Blueprint('main', __name__)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route("/", methods=["GET", "POST"])
@login_required
def musicapp():
    # get the music list from the database with scalars
    #music_list = db.session.scalars(sa.select(Music)).all()

    # get the music_list but only for the logged in user
    music_list = db.session.scalars(sa.select(Music).where(Music.user_id == current_user.id)).all()

    form = MusicForm()
    if form.validate_on_submit():
        music = Music()
        music.user_id = current_user.id
        music.title = form.title.data
        music.url = form.url.data
        music.monitored = form.monitored.data
        music.interval = form.interval.data
        db.session.add(music)
        db.session.commit()
        flash('Song added')
        return redirect(url_for('musicapp'))

    return render_template("musicapp.html", music_list=music_list, form=form)
    #return "musicapppage"

@app.route("/add", methods=["POST"])
@login_required
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
    return redirect(url_for("musicapp"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('musicapp'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('musicapp')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('musicapp'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('musicapp'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/monitor/<int:music_id>")
@login_required
def monitor(music_id):
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()

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
            # add flash message to confirm the interval change
            flash('Monitoring: On for ' + str(music.title))
        elif music.monitored is False:
            print("monitor is OFF")
            print("Going to delete the scheduled job")
            #print(music.monitored)
            # delete the scheduled job for the deleted playlist/song
            deleteJobs(music.id)
            # add flash message to confirm the interval change
            flash('Monitoring: Off for ' + str(music.title))
    return redirect(url_for("musicapp"))

@app.route("/delete/<int:music_id>")
@login_required
def delete(music_id):

    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()

    # check if song exists
    if music is None:
        flash('Song not found')
        return redirect(url_for("musicapp"))
    
    # check if the user is the owner of the song
    #print("music user id:", music.user_id)
    #print("current user id:", current_user.id)
    if music.user_id != current_user.id:
        flash('You cannot delete songs of others!')
        return redirect(url_for("musicapp"))

    # delete the music object from the database
    db.session.delete(music)
    db.session.commit()
    # delete the scheduled job for the deleted playlist/song
    deleteJobs(music_id)
    return redirect(url_for("musicapp"))

@app.route("/download/<int:music_id>")
@login_required
def download(music_id):
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()
    # execute the download function to download one time
    if music is not None and settings is not None:
        immediateJob(music, settings)
    return redirect(url_for("musicapp"))

# let users configure their interval value on a per playlist/song basis
@app.route("/interval/<int:music_id>")
@login_required
def interval(music_id):
    
    # at the moment it accepts everything. but it should only allow integers as input.
    # close this down somewhere so only integers are allowed through this method.
    interval = request.args.get('interval', None) # None is the default value if no interval is specified
    
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()


    # get the CloudStorage settings from the database with scalars
    settings = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.id == music_id)).first()

    # settings = WebDAV.query.filter_by(id=1).first()


    if music:
        music.interval = interval
        db.session.commit()
        #print(interval)

        # add flash message to confirm the interval change
        flash('Interval changed to ' + str(interval) + ' minutes')
        
        # if the monitor is on, then reschedule the job with the new interval value
        if music.monitored is True:
            print("Going to reschedule the music to be downloaded on repeat")
            # delete the scheduled job for the deleted playlist/song
            deleteJobs(music_id)
            # schedule a job for the newly added playlist/song with the corrosponding interval value
            scheduleJobs(music, settings)

    return redirect(url_for("musicapp"))

# this function can get the time left before the playlist will be downloaded again
@app.route("/intervalstatus/<int:music_id>")
@login_required
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

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    #    title = "Settings"


    # make a form to add the webdav settings to the webdav_storage table
    
    # create a form to add the settings
    # WebDAVform = WebDAV()
    # if WebDAVform.validate_on_submit():
    #     storagesettings = CloudStorage()
    #     storagesettings.protocol_type = "webdav_storage"
    #     storagesettings.user_id = current_user.id

    #     storagesettings.WebdavStorage.url = WebDAVform.url.data
        
    #     storagesettings.url = WebDAVform.url.data
    #     storagesettings.directory = WebDAVform.directory.data
    #     storagesettings.username = WebDAVform.username.data
    #     storagesettings.password = WebDAVform.password.data
    #     db.session.add(storagesettings)
    #     db.session.commit()
    #     flash('WebDAV account added!')
    #     return redirect(url_for('settings'))
    

    WebDAVform = WebDAV()
    if WebDAVform.validate_on_submit():
        WebDAVSettings = WebDavStorage()
        WebDAVSettings.url = WebDAVform.url.data
        WebDAVSettings.directory = WebDAVform.directory.data
        WebDAVSettings.username = WebDAVform.username.data
        WebDAVSettings.password = WebDAVform.password.data

        WebDAVSettings.user_id = current_user.id
        WebDAVSettings.protocol_type = "webdav_storage"

        db.session.add(WebDAVSettings)
        db.session.commit()
        flash('WebDAV account added!')
        return redirect(url_for('settings'))


    # get the CloudStorage settings from the database with scalars
    #cloudstorageaccounts = db.session.scalars(sa.select(CloudStorage)).all()

    # get the CloudStorage settings from the database with scalars for the logged in user
    cloudstorageaccounts = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.user_id == current_user.id)).all()

    for cloudstorageaccount in cloudstorageaccounts:
        print(cloudstorageaccount)
        print(cloudstorageaccount.id)
        print(cloudstorageaccount.owner)
        print(cloudstorageaccount.protocol_type)

        # print the settings for the webdav_storage protocol
        # if cloudstorageaccount.protocol_type == "webdav_storage":
        #     print(cloudstorageaccount.webdav_storage.url)
        #     print(cloudstorageaccount.directory)
        #     print(cloudstorageaccount.username)
        #     print(cloudstorageaccount.password)
    
    # webdavstor = sa.select(WebDavStorage).order_by(WebDavStorage.id)
    # storages = db.session.scalars(webdavstor).all()
    # for storage in storages:
    #     print("hier zijn de storages")
    #     print(storages)
    #     print("einde storages")
    #     print(storage.url)
    #     print(storage.directory)
    #     print(storage.username)
    #     print(storage.password)
 


    # storages = sa.select(CloudStorage).order_by(CloudStorage.id)
    # objects = db.session.scalars(storages).all()
    # for object in objects:
    #     if object.protocol_type == "webdav_storage":
    #         print("hier zijn de objects")
    #         print(object)
    #         print("einde objects")
    #         print(object.url)
    #         print(object.directory)
    #         print(object.username)
    #         print(object.password)
   
    #print("hier zijn de objects")
    #print(objects)
    #print("einde objects")


    # # get and print webdave_storage settings
    # webdav = db.session.scalars(sa.select(WebDavStorage)).all()
    # for webdav in webdav:
    #     print("deze loop")
    #     print(webdav.url)
    #     print(webdav.directory)
    #     print(webdav.username)
    #     print(webdav.password)


        #if cloudstorageaccount.protocol_type == "webdav_storage":
        #    print(cloudstorageaccount.webdav_storage.url)
        #    print(cloudstorageaccount.directory)
        #    print(cloudstorageaccount.username)
        #    print(cloudstorageaccount.password)



    # get songs archive
    #with open(r"../download_archive/downloaded", 'r') as songs:
    #    songs = songs.readlines()
    #    # add song ID's so they are easy to delete/correlate
    #    songs = list(enumerate(songs))
    
    # still going to save songs in a text file? or in the database?
    songs = ["youtube 4975498", "youtube 393judjs", "soundcloud 93034303"]
    songs = list(enumerate(songs))


    return render_template("settings.html", cloudstorageaccounts=cloudstorageaccounts, songs=songs, WebDAVform=WebDAVform, title='Settings')


@app.route("/settings/delete/<int:cloudstorage_id>")
@login_required
def deleteStorageAccount(cloudstorage_id):
    # get the music object from the database with scalars
    cloudstorage_id = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.id == cloudstorage_id)).first()
    db.session.delete(cloudstorage_id)
    db.session.commit()
    # add flash message to confirm the interval change
    flash('CloudStorage account deleted')
    return redirect(url_for("settings"))


@app.route("/settings/save", methods=["POST"])
@login_required
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

@app.route("/archiveaddsong", methods=["POST"])
@login_required
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

@app.route("/archivedeletesong/<int:song_id>")
@login_required
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

@app.route('/archivedownload') # GET request
@login_required
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
@app.route("/archiveupload", methods=["POST"])
@login_required
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