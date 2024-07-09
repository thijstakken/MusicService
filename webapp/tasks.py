# youtube-dl stuff
from yt_dlp import YoutubeDL
import time
from rq import get_current_job
from webapp import db, create_app
import sqlalchemy as sa
from webapp.models import MusicTask, Music, CloudStorage, WebDavStorage
#from webapp import current_app

# uploading files to a server logic
import os
import requests


# def example(seconds):
#     job = get_current_job()
#     print('Starting task')
#     for i in range(seconds):
#         job.meta['progress'] = 100.0 * i / seconds
#         job.save_meta()
#         print(i)
#         time.sleep(1)
#     job.meta['progress'] = 100
#     job.save_meta()
#     print('Task completed')


#webapp = create_app()
#webapp.app_context().push()

def downloadmusic(music_id, username):
    # the function needs an app context, because it needs to work with the database
    # the solution used here is to start a new app context, so we can work with the database

    # create a new app context
    # submit a option in the function that will stopsome of the create_app functions, like starting background tasks again, because this will cause a loop
    app = create_app(baseconfig=True)
    # we always need to have the app context to work with the database
    # this whole function is run from the redis worker, which is a seperate process from the main app
    with app.app_context():
    
        print('this is username original', username)
        music = db.session.get(Music, music_id)

        # get the username that owns the music
        usernametest = music.musicowner.username

        print("Username new one:", usernametest)
        print("Username:", usernametest)
        print("Username:", usernametest)
        print("Username:", usernametest)

        #music = db.session.scalars(sa.select(MusicTask).where(MusicTask.id == music_id)).first()
        print("Downloading music...", music.url)
        print("")
        print("Downloading playlist...", music_id)
        #downloadPlaylists(ydl_opts, url)
        try:
            _set_task_progress(0)

            # we want to look at the music object and get the DownloadedSongs object

            # we want to put the contents in a text file so YT-DLP can work with it
            # path: /music/{username}/download_archive.txt, then put the contents in there


            # get the playlist name of an url with yt-dlp    
            # this has so far proofed to not be reliable, will use a standard archive location for ALL playlists
            # youtube-dlp is designed to work with a single static download_archive, not multiple ones, so therefore a lot of custom code should be worked out.
            # Use the title of the playlist (if present) as the folder name
            # Configure YouTube DL options for the title extraction


            # ydl_title = {
            #     'dump_single_json': True,
            #     'extract_flat': True,
            # }

            # with YoutubeDL(ydl_title) as ydl:
            #     info = ydl.extract_info(music.url, download=False)
            #     #print("Info:", info)
            #     # Check if the extracted info is for a playlist
            #     if info.get('_type') == 'playlist':
            #         # It's a playlist, get the playlist title
            #         playlistname = info.get('title', None)
            #         print("This is a playlist, the name is:", playlistname)
            #     else:
            #         # It's not a playlist, ignore the output
            #         print("Not a playlist, ignoring output.")
            #         # set the playlistname to NA, because it's not a playlist, yt-dlp will use the NA folder for music that has no playlist title
            #         playlistname = "NA"
            #     # get an item from the info dictionary

            #     #playlistname = info.get('title', None)
                
            #     #playlistname = info.get('playlist', None)
            #     print("Title name is:", playlistname)
            #     #print("Playlist name:", playlistname)
            #     #print("Playlist name:", playlistname)


            # create the music directory for the user
            #path = f'./music/{username}/{playlistname}'

            path = f'./music/{username}'

            #archivefilename = f'%(playlist)s/download_archive.txt'
            archivefilename = '/download_archive.txt'

            # create the directory if it does not exist
            if not os.path.exists(path):
                os.makedirs(path)
                print("Directory ", path, " Created ")

            #combine path and file into one path
            fullpath = path + archivefilename
            #print('This is the full archive path for all playlists', fullpath)

            ydl_opts['download_archive'] = fullpath # this will update the downloads file which serves as a database/archive for which songs have already been downloaded, so it don't downloads them again
            
            # output template for the downloaded music
            musicpath = f'{path}/%(playlist)s/%(title)s-%(id)s.%(ext)s'
            ydl_opts['outtmpl'] = musicpath # save music to the /music folder. and it's corrosponding folder which will be named after the playlist name

            # we want to download the music from the URL
            with YoutubeDL(ydl_opts) as ydl:
                    #print(ydl_opts)
                    ydl.download(music.url)


            # we want to remove the text file from the local storage


            # determine where the music should go next
            # if the user has no storage account configured we want to store the music locally as a fallback/default option
            # if the user has a local storage account, we want to store the music locally
            # if the user has a cloud storage account, we want to upload the music to the cloud

            # Assuming music.musicowner is the user object you want to filter by
            
            
            #storages = db.session.scalars(
            #    CloudStorage.query.filter(CloudStorage.storageowner == music.musicowner)).all()

            storages = db.session.scalars(
                sa.select(CloudStorage).where(CloudStorage.storageowner == music.musicowner)).all()
            
            # check if there are more then one storage accounts configured
            # the app can only handle one storage account at a time, so we want to check if there are more then one storage account configured
            if len(storages) > 1:
                print("More then one storage account found")
                print("The app can only handle one storage account at a time")
                print("Please remove the extra storage accounts")
                print("Stopping the download...")
                return

            print("This is the storage object:", storages)
            if storages:
                for storage in storages:
                    print("This is the storage protocol:", storage.protocol_type)

                    if storage.protocol_type == "webdav_storage":
                        # get the cloud storage account settings for webdav
                        webdavsettings = db.session.scalars(sa.select(WebDavStorage).where(WebDavStorage.id == storage.id)).first()
                        print("This is the webdav object", webdavsettings)
                        webdav(webdavsettings.url, webdavsettings.username, webdavsettings.password, webdavsettings.directory)


                    if storage.protocol_type == "local_storage":
                        localmusic()

            else:
                # if there a no cloud storage accounts configured, we want to store the music locally
                print("No cloud storage accounts found")
                print("Storing music in local storage...")
                # Logic to handle when no cloud storages are found
                ### NO LOGIC NEEDED, SINCE THE MUSIC IS ALREADY STORED LOCALLY BY DEFAULT ###
                pass
            
            #if music.musicowner.cloud_storages == 'local':
            #    print("User has local storage configured")
            #    print("Moving music to local storage...")

            _set_task_progress(100)
        except Exception:
            _set_task_progress(100)
            #webapp.logger.error('Unhandled exception', exc_info=sys.exc_info())
            print("Error downloading the playlist")
            print("")
        finally:
            _set_task_progress(100)
            # some cleanup
            print("Cleaning up...")
            print("Downloading complete for:", music_id)
            print("")

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
    'simulate': False,                                              # to dry test the YT-DL, if set to True, it will skip the downloading. Can be True/False
    'cachedir': False,                                              # turn off caching, this should mitigate 403 errors which are commonly seen when downloading from Youtube
    'nocheckcertificates': True,                                    # mitigates YT-DL bug where it wrongly examins the server certificate, so therefore, ignore invalid certificates for now, to mitigate this bug
}


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = db.session.get(MusicTask, job.get_id())
        #task.user.add_notification('task_progress', {'task_id': job.get_id(),
        #                                             'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()



# webdav

def webdav(url, username, password, directory):
    print("User has WebDAV storage configured")
    print("Moving music to WebDAV storage...")
    
    print("This is the storage URL:", url)
    print("This is the storage directory:", directory)
    print("This is the storage username:", username)
    print("This is the storage password:", password)
    print("This is the webdav function")
    print("Music moved to WebDAV storage")

    # this function will call all sub functions in order

# start uploading the music to the cloud using WebDAV
def uploadmusic(url, username, password, remoteDirectory):
    # Whenever the function is called it will upload all music present in the local music folder
    # At the moment it does not make a distinction between songs from other jobs, it will just upload everything...
    
    # THIS IS TEMPORARY ###
    localDirectory = 'music'
    ###

    print("")
    print('Creating cloud folder structure based on local directories...')
    create_folders(localDirectory, remoteDirectory, url, username, password)

    print("")
    print('Uploading music into the cloud folders...')
    upload_music(remoteDirectory, url, username, password)

    # deleting files is already don in the upload_music function... the delete part could be in a seperate function.

    #print("Clearing local MP3 files since they are no longer needed...")
    #clear_local_music_folder()


# creates directories in the cloud based on the local directory structure
def create_folders(localDirectory, remoteDirectory, url, username, password):
    
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
def upload_music(remoteDirectory, url, username, password):
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



# local music storage

def localmusic():
    print("User has local storage configured")
    print("Moving music to local storage...")
    print("This is the localmusic function")
    # this function basically does not have to do anything since the music is already stored locally by default now
    print("Music moved to local storage")

    # this function will call all sub functions in order

# ftp/sftp