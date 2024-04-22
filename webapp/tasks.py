# youtube-dl stuff
from yt_dlp import YoutubeDL
import time
from rq import get_current_job
from webapp import db, create_app
from webapp.models import MusicTask
import sys

webapp = create_app()
webapp.app_context().push()

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


def downloadmusic(music_id, url):
    print("")
    print("Downloading playlist...", music_id)

    downloadPlaylists(ydl_opts, url)

    print("Downloading complete for:", music_id)
    print("")

# download the playlists
def downloadPlaylists(ydl_opts, url):
    try:
        _set_task_progress(0)
        with YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
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