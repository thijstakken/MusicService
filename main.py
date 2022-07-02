from __future__ import unicode_literals
from re import L
import youtube_dl
import shutil
import requests
import os
from pathlib import Path

class MyLogger(object):
    def debug(self, msg):   # print debug
        print(msg)
        #pass

    def warning(self, msg): # print warnings
        print(msg)
        #pass

    def error(self, msg):   # always print errors
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'writethumbnail': True,
    'format': 'bestaudio[asr<=44100]/best[asr<=44100]', # using asr 44100 as max, this mitigates exotic compatibility issues with certain mediaplayers
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        #'preferredquality': '192',                     # with not specifying a preffered quality, the original bitrate will be used, therefore skipping one unnecessary conversion and keeping more quality
        },
    {'key': 'EmbedThumbnail',},                         # embed the Youtube thumbnail with the MP3 as coverart.
    ],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': './music/%(playlist)s/%(title)s.%(ext)s',# save music to the /music folder. and it's corrosponding folder which will be named after the playlist name
    'simulate': False,                                  # to dry test the YT-DL, if set to True, it will skip the downloading. Can be True/False
    'cachedir': False,                                  # turn off caching, this should mitigate 403 errors which are commonly seen when downloading from Youtube
    'download_archive': './database/downloaded.txt',    # this will update the .txt file which serves as a database for which files have already been downloaded
    'nocheckcertificate': True,                         # mitigates YT-DL bug where it wrongly examins the server certificate, so therefore, ignore invalid certificates for now, to mitigate this bug
}


def getPlaylistURLs():
# reads and saves playlist URL's in a list
    with open('./database/playlists.txt') as file:
        lines = [line.rstrip() for line in file]
    return(lines)

def downloadPlaylists(ydl_opts, lines):
# downloads the playlists one by one
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(lines)

# Nextcloud uses a webdav API, and therefore you must create the folder structure first
# only after creating the folder, you can then put the music files into them
# create directories in the cloud based on the local structure
# first create the initial music folder
def create_folders(localDirectory):
    
    # for every (music) playlist create an directory at the users remote directory
    for localDirectory, dirs, files in os.walk(localDirectory):
        for subdir in dirs:
            #print('localdir ' + localDirectory)
            print(os.path.join(localDirectory, subdir))
            #print('subdir ' + subdir)

            fullurl = url + remoteDirectory + subdir

            r = requests.request('MKCOL', fullurl, auth=(username, password))
            print(r.text)
            print("And the url used:")
            print(r.url)


# after the neccessary directories have been created we can start to put the music into the folders
# iterate over files and upload them to the corrosponding folder in the cloud
def upload_music(remoteDirectory):
    
    for root, dirs, files in os.walk(localDirectory):
        for filename in files:
            
            # get full path to the file (example: 'music/example playlist/DEAF KEV - Invincible [NCS Release].mp3')
            path = os.path.join(root, filename)
            
            # get the folder name in which the file is located (example: 'example playlist')
            subfoldername = os.path.basename(os.path.dirname(path))
            
            # if the subfoldername is music, is appears that it's a file at that directory
            # in order to mitigate the file getting lost, because there does not exist an music folder in the cloud directory
            # set is to an empty string so that the file will end up at the root of the remote_directory in de cloud
            # this is a shitty mitigation, have to implement a better one, if somebodies playlist is called 'music', all files will go to the wrong place also...
            if subfoldername == 'music':
                subfoldername = ''


            #print("This is REMOTE_DIRECTORY")
            #print(remoteDirectory)

            #print("This is ROOT:")
            #print(root)

            # construct the full url so we can PUT the file there
            fullurl = url + remoteDirectory + subfoldername + '/' + filename
            
            #path = root+'/'+filename
            #print('to ' + fullurl + '\n' + path)
            #openBin = {'file':(filename,open(path,'rb').read())}
            #headers = {'Content-type': 'text/plain', 'Slug': filename}
            
            headers = {'Slug': filename}
            r = requests.put(fullurl, data=open(path, 'rb'), headers=headers, auth=(username, password))
            
            print(r.text)
            print("And the url used:")
            print(r.url)

def clear_local_music_folder():
    # when uploading the files is done, the local music folder should be cleared to save space
    # this clears the local music folder so MP3's do not pile up locally, there is no point in storing them anymore since they have been uploaded to cloud storage already
    dir = './music/'
    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


if __name__ == '__main__':
    # get the OS enviroment variabels and save them to local variabels
    # these enviroment variabels get passed by the docker run command
    localDirectory = os.getenv('LOCAL_DIRECTORY')              # 'music' always use music as local, this can't be changed at the moment, due to some hardcoding
    remoteDirectory = os.getenv('REMOTE_DIRECTORY')            # Nextcloud folder where you want to save your music
    url = os.getenv('URL')                                     # Nextcloud URL
    username = os.getenv('NCUSERNAME')                         # Nextcloud username
    password = os.getenv('NCPASSWORD')                         # Nextcloud password

    print("Fetching playlist URL's...")
    lines = getPlaylistURLs()
    print(lines)

    print("Downloading playlists...")
    downloadPlaylists(ydl_opts, lines)

    print('Creating cloud folder structure based on local directories...')
    create_folders(localDirectory)

    print('Uploading music into the cloud folders...')
    upload_music(remoteDirectory)

    print("Clearing local MP3 files since they are no longer needed")
    clear_local_music_folder()

    print("Finished running music service")