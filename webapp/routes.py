from __future__ import unicode_literals
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, Blueprint
from flask_login import current_user, login_required
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
import threading

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


### START OF SETTINGS ###

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

### END OF SETTINGS ###



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