# schedule stuff
import schedule
import time
from webapp.tasks import downloadmusic
from webapp.uploadMusic import uploadmusic


def download_and_upload(music, settings):
    if music is not None:
        # call download function and pass the music_id we want to download to it
        downloadmusic(music.id, music.url)

    if settings is not None:   
        # call upload function to upload the music to the cloud
        uploadmusic(settings.WebDAV_URL, settings.WebDAV_Username, settings.WebDAV_Password, settings.WebDAV_Directory)

    # if tag immidiate is present, then delete the job after it has run once
    # if the job that is executed contains the tag 'immidiate' then cancel the job after it has run once
    # we need to remove the immidiate job (download now button/manual) from the schedule because otherwise it will keep running every second
    if schedule.get_jobs(tag='immidiate'):
        print("Going to delete immidiate job:", music.id)
        return schedule.CancelJob

# function which will keep an interval time for each playlist/song in the background
# this will be used to check if the playlist/song needs to be downloaded again
# if the interval time has passed, then the playlist/song will be downloaded again
# this will be used to keep the music up to date
# this only schedules jobs for playlists that already exist in the database on boot
def scheduleJobs(music, settings):
    # https://github.com/dbader/schedule
    # https://schedule.readthedocs.io/en/stable/
    schedule.every(music.interval).minutes.do(download_and_upload,music,settings).tag(music.id)
    print("Interval set for:", music.title, music.interval, "minutes")

def immediateJob(music, settings):
    # Schedule the download_and_upload function to run immediately
    schedule.every().second.do(download_and_upload,music,settings).tag(music.id, 'immidiate')
    print("Immediate job set for:", music.title, "executing now")

# delete scheduled jobs when they are no longer needed
def deleteJobs(music_id):
    #print('here are all CURRENT jobs', schedule.get_jobs())
    schedule.clear(music_id)
    print("Deleted job for:", music_id)
    #print('here are all jobs NOW', schedule.get_jobs())

# this functions runs in a seperate thread to monitor scheduled jobs and run them when needed
def run_schedule(app_context):
    app_context.push()
    # run the schedule in the background
    while True:
        schedule.run_pending()
        time.sleep(1)


# only if the schedule is turned on, then the music should be on a schedule
# code example for later use
#    for (complete, ) in db.session.query(Music.complete).filter_by(id=music_id):
#                if complete == True:
                    # then turn on the monitor schedule

#                    print("monitor is ON")
#                    print("Going to upload the music to the cloud account")
#                    print(complete)


#                else:
#                    print("monitor is OFF")
#                    print("NOT uploading songs because monitor is turned off")
#                    print(complete)
