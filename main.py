from __future__ import unicode_literals
from re import L
from pyparsing import line
import youtube_dl
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
    'download_archive': './downloaded.txt',    # this will update the .txt file which serves as a database for which files have already been downloaded
    'nocheckcertificate': True,                         # mitigates YT-DL bug where it wrongly examins the server certificate, so therefore, ignore invalid certificates for now, to mitigate this bug
}


def getPlaylistURLs():
# reads and saves playlist URL's in a list
    with open('./playlists.txt') as file:
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
    # create the "music" folder in cloud storage
    fullurl = url + username + '/' + 'music'
    r = requests.request('MKCOL', fullurl, auth=(username, password))
    print(r.text)
    print("and the url used:")
    print(r.url)

    # and for every subfolder (genre) create it inside of the music folder
    for localDirectory, dirs, files in os.walk(localDirectory):
        for subdir in dirs:
            #print('localdir ' + localDirectory)
            print(os.path.join(localDirectory, subdir))
            #print('subdir ' + subdir)
        
            fullurl = url + username + '/' + 'music' + '/' + subdir
            r = requests.request('MKCOL', fullurl, auth=(username, password))
            print(r.text)
            print("and the url used:")
            print(r.url)


# after the neccessary directories have been created we can start to put the music into the folders
# iterate over files and upload them to the corrosponding folder in the cloud
def upload_music():
    for root, dirs, files in os.walk(localDirectory):
        for filename in files:
            path = os.path.join(root, filename)

            print(root)
            fullurl = url + username + '/' + root + '/' + filename
            #path = root+'/'+filename
            print('to ' + fullurl + '\n' + path)
            #openBin = {'file':(filename,open(path,'rb').read())}
            #headers = {'Content-type': 'text/plain', 'Slug': filename}
            headers = {'Slug': filename}
            r = requests.put(fullurl, data=open(path, 'rb'), headers=headers, auth=(username, password))
            print(r.text)
            print("and the url used:")
            print(r.url)


if __name__ == '__main__':

    # get the OS enviroment variabels and save them to local variabels
    # these enviroment variabels get passed by the docker run command
    localDirectory = os.getenv('LOCAL_DIRECTORY')              #'music' always use music as local, this can't be changed at the moment, due to some hardcoding
    remoteDirectory = os.getenv('REMOTE_DIRECTORY')            # Nextcloud folder where you want to save your music
    url = os.getenv('URL')                                     # Nextcloud URL
    username = os.getenv('NCUSERNAME')                         # Nextcloud username
    password = os.getenv('NCPASSWORD')                         # Nextcloud password

    #print("SHOWING VARIABELS, for debugging:")
    #print(localDirectory)
    #print(remoteDirectory)
    #print(url)
    #print(username)
    #print(password)

    print("Fetching playlist URL's...")
    lines = getPlaylistURLs()
    print(lines)

    print("Downloading playlists...")
    downloadPlaylists(ydl_opts, lines)

    print('Creating cloud folder structure based on local directories...')
    create_folders(localDirectory)

    print('Uploading music into the cloud folders...')
    upload_music()


# print "Here is your link to the file: " + link_info.get_link()