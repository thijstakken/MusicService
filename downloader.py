from __future__ import unicode_literals
import youtube_dl


class MyLogger(object):
    def debug(self, msg):   #Debug printen
        print(msg)
        #pass

    def warning(self, msg): #Waarschuwingen printen
        print(msg)
        #pass

    def error(self, msg):   #Errors altijd printen
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'writethumbnail': True,
    'format': 'bestaudio[asr<=44100]/best[asr<=44100]',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        #'preferredquality': '192',                     #With not specifying a preffered quality, the original bitrate will be used
        },
    {'key': 'EmbedThumbnail',},
    ],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': '.\Music\%(playlist)s\%(title)s.%(ext)s',
    'simulate': False,                                  #Droog oefenen indien True, niks downloaden, opties zijn True/False
    'cachedir': False,                                  #Zet caching uit om 403 Forbidden errors te voorkomen
    'download_archive': '.\Database\downloaded.txt',    #Vastleggen of een muziekje als gedownload is
    'nocheckcertificate': True,                         #Verifiërt niet of het SSL certificaat geldig is, dit voorkomt een onterechte foutmelding die ik een keer had
}

#Haalt playlist URL's op en zet ze in een lijst
with open('./Database/playlists.txt') as file:
    lines = [line.rstrip() for line in file]        #Leest lijn voor lijn de playlists in van playlist.txt

print(lines)

#Gaat elke playlist downloaden
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(lines)