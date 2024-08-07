from flask import render_template, flash, redirect, url_for, request, current_app, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from webapp import db
from webapp.settings import bp
import os

from webapp.settings.forms import WebDAVForm, LocalStorageForm

from flask_login import current_user, login_required
import sqlalchemy as sa
from webapp.models import CloudStorage, WebDavStorage, LocalStorage


from werkzeug.utils import secure_filename
from sqlalchemy import select


@bp.route('/profile')
@login_required
def profile():
    return render_template('settings/profile.html')


### START OF SETTINGS ###

@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    # create the download_archive if it does not exist
    if current_user.is_authenticated:
        # check if the archive file exists, if not create it
        path = os.path.join('./music', current_user.username)
        archivefilename = 'download_archive.txt'
        fullpath = os.path.join(path, archivefilename)

        # create the directory if it does not exist
        if not os.path.exists(path):
            os.makedirs(path)
            print("Directory ", path, " Created ")
        
        # create the download_archive.txt
        if not os.path.exists(fullpath):
            with open(fullpath, 'w') as file:
                file.write('')


    # get the CloudStorage settings from the database with scalars for the logged in user
    cloudstorageaccounts = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.user_id == current_user.id)).all()

    for cloudstorageaccount in cloudstorageaccounts:
        print(cloudstorageaccount)
        print(cloudstorageaccount.id)
        print(cloudstorageaccount.storageowner)
        print(cloudstorageaccount.protocol_type)        

    WebDAVform = WebDAVForm()
    if WebDAVform.validate_on_submit():
        if cloudstorageaccounts:
            flash('You already have a sync profile configured. Please delete the current profile before adding a new one.')
            return redirect(url_for('settings.settings'))
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
        return redirect(url_for('settings.settings'))
    
    # this form is used to add a local storage account
    LocalStorageform = LocalStorageForm()
    if LocalStorageform.validate_on_submit():
        if cloudstorageaccounts:
            flash('You already have a sync profile configured. Please delete the current profile before adding a new one.')
            return redirect(url_for('settings.settings'))
        LocalStorageSettings = LocalStorage()
        LocalStorageSettings.user_id = current_user.id
        LocalStorageSettings.protocol_type = "local_storage"
        db.session.add(LocalStorageSettings)
        db.session.commit()
        flash('Local account added!')
        return redirect(url_for('settings.settings'))
    


    # get the CloudStorage settings from the database with scalars
    #cloudstorageaccounts = db.session.scalars(sa.select(CloudStorage)).all()

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



    # have to start using the following, where are using a text file, this is simple and native to yt-dlp
    # therefore we can find the download archive for each user here:
    # /music/{username}/download_archive.txt
    # get songs archive

    # get current username
    username = current_user.username

    path = f"./music/{username}/download_archive.txt"

    with open(path, 'r') as songs:
       songs = songs.readlines()
       # add song ID's so they are easy to delete/correlate
       songs = list(enumerate(songs))

    # test code:
    #songs = ["youtube 4975498", "youtube 393judjs", "soundcloud 93034303"]
    #songs = list(enumerate(songs))

    return render_template("settings/settings.html", cloudstorageaccounts=cloudstorageaccounts, songs=songs, WebDAVform=WebDAVform, LocalStorageform=LocalStorageform, title='Settings')


@bp.route("/settings/delete/<int:cloudstorage_id>")
@login_required
def deleteStorageAccount(cloudstorage_id):
    # get the music object from the database with scalars
    cloudstorage = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.id == cloudstorage_id)).first()
    db.session.delete(cloudstorage)
    db.session.commit()
    # add flash message to confirm the interval change
    flash('CloudStorage account deleted')
    return redirect(url_for("settings.settings"))

### END OF SETTINGS ###


### ARCHIVE FUNCTIONS ###

@bp.route("/archiveaddsong", methods=["POST"])
@login_required
def archiveaddsong():
    song = request.form.get("song")

    path = os.path.join('./music', current_user.username)
    archivefilename = 'download_archive.txt'
    fullpath = os.path.join(path, archivefilename)

    # create the directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory ", path, " Created ")

    # get archive for analysis
    with open(fullpath) as file:
        text = file.read()

    # add new song to archive
    with open(fullpath, 'a') as archive:
        # check if a newline already exists
        if not text.endswith('\n'):
            # if it does not end with a newline, then add it
            archive.write('\n')
        # add song if it is not None
        if song is not None:
            archive.write(song)
            archive.write('\n')
    return redirect(url_for("settings.settings"))

@bp.route("/archivedeletesong/<int:song_id>")
@login_required
def archivedeletesong(song_id):

    path = os.path.join('./music', current_user.username)
    archivefilename = 'download_archive.txt'
    fullpath = os.path.join(path, archivefilename)

    # create the directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory ", path, " Created ")

    # get songs archive
    with open(fullpath, 'r') as fileop:
        songs = fileop.readlines()

    # delete/clear the correct row
    with open(fullpath , 'w') as fileop:
        for number, line in enumerate(songs):
        # delete/clear the song_id line
            if number not in [song_id]:
                fileop.write(line)
    
    flash('Song deleted from archive')

    return redirect(url_for("settings.settings"))

@bp.route('/archivedownload') # GET request
@login_required
# based on flask.send_file method: https://flask.palletsprojects.com/en/2.3.x/api/#flask.send_file
def archivedownload():

    path = os.path.join('./music', current_user.username)
    archivefilename = 'download_archive.txt'
    fullpath = os.path.join(path, archivefilename)

    # create the directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)
        print("Directory ", path, " Created ")

    # Convert the relative path to an absolute path
    # the send file funcion requires an absolute path
    absolute_path = os.path.abspath(fullpath)

    return send_file(
        absolute_path,
        mimetype='text/plain',
        download_name='download_archive.txt',
        as_attachment=True
    )

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# used flask uploading files guide https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
@bp.route("/archiveupload", methods=["POST"])
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

            path = os.path.join('./music', current_user.username)
            archivefilename = 'download_archive.txt'
            fullpath = os.path.join(path, archivefilename)

            # create the directory if it does not exist
            if not os.path.exists(path):
                os.makedirs(path)
                print("Directory ", path, " Created ")

            # read existing archive
            with open(fullpath) as archive_data:
                text = archive_data.read()

            # add new songs to archive
            with open(fullpath, 'a') as archive:
                
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

            return redirect(url_for('settings.settings'))
  
### END ARCHIVE FUNCTIONS ###