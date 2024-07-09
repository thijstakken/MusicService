from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
import sqlalchemy as sa
from webapp import db
# from webapp.main.forms import MusicForm, CloudStorageForm ???
from webapp.models import Music, CloudStorage, MusicTask, User
from webapp.main import bp
import datetime
import schedule
from webapp.scheduler import scheduleJobs, deleteJobs
from datetime import datetime

### commented out because of circular import, going to refactor this later, so will be fixed then.
#from webapp.downloadScheduler import scheduleJobs, deleteJobs, immediateJob, run_schedule
from webapp.main.forms import MusicForm

@bp.route("/", methods=["GET", "POST"])
@login_required
def musicapp():

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
        return redirect(url_for('main.musicapp'))

    # get the schedule with tag music.id
    print("All jobs", schedule.get_jobs())

    scheduledJobs = schedule.get_jobs()

    # print the next run time for each scheduled job
    for job in scheduledJobs:
        print("Next run time for job:", job.next_run)
        # print the tag for the job
        print("Tag for job:", job.tags)
        # the job.next_run is an datetime object
        # convert the datetime format into the ISO 8601 format
        # this is needed for the frontend to display the time correctly
        #job.next_run = job.next_run.strftime('%Y-%m-%dT%H:%M:%SZ')  # Adjust format as needed

        # job.next_run = job.next_run.isoformat()
        
        # it's using the local time, not the UTC time
        # so we need to adjust the time to the UTC time
        # this is needed for the frontend to display the time correctly
        
        #job.next_run = job.next_run.strftime('%Y-%m-%dT%H:%M:%SZ')

        #job_next_run_datetime = datetime.strptime(job.next_run, '%Y-%m-%d %H:%M:%S.%f')

        #job.next_run = job_next_run_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')  # Adjust format as needed

        # print the next run time for the job
        print("This is the ADJUSTED run time for job:", job.next_run)
        

    return render_template("musicapp.html", music_list=music_list, form=form, scheduledJobs=scheduledJobs)

@bp.route("/add", methods=["POST"])
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
    return redirect(url_for("main.musicapp"))

@bp.route("/monitor/<int:music_id>")
@login_required
def monitor(music_id):
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()

    # turned below rule off because during startup the settings are already set.
    #settings = WebDAV.query.filter_by(id=1).first()
    if music is not None:
        music.monitored = not music.monitored
        db.session.commit()
        #if music.monitored is True and settings is not None:
        if music.monitored is True:
            print("monitor is ON")
            print("Going to schedule the music to be downloaded on repeat")
            print(music.monitored)
            # schedule a job for the newly added playlist/song with the corrosponding interval value
            #scheduleJobs(music, settings)
            
            scheduletask(music)

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
    return redirect(url_for("main.musicapp"))

@bp.route("/delete/<int:music_id>")
@login_required
def delete(music_id):

    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()

    # check if song exists
    if music is None:
        flash('Song not found')
        return redirect(url_for("main.musicapp"))
    
    # check if the user is the owner of the song
    #print("music user id:", music.user_id)
    #print("current user id:", current_user.id)
    if music.user_id != current_user.id:
        flash('You cannot delete songs of others!')
        return redirect(url_for("main.musicapp"))

    # delete the music object from the database
    db.session.delete(music)
    db.session.commit()
    # delete the scheduled job for the deleted playlist/song
    deleteJobs(music_id)
    return redirect(url_for("main.musicapp"))

@bp.route("/download/<int:music_id>")
@login_required
def download(music_id):
    # get the music object from the database with scalars
    #music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()

    # set actiontype to False, because this is a manual download
    # true is only used for scheduled (or "automated") downloads
    actiontype = False
    # download the music
    downloadmusicAction(music_id, actiontype)

    return redirect(url_for("main.musicapp"))

# let users configure their interval value on a per playlist/song basis
@bp.route("/interval/<int:music_id>")
@login_required
def interval(music_id):
    
    # at the moment it accepts everything. but it should only allow integers as input.
    # close this down somewhere so only integers are allowed through this method.
    interval = request.args.get('interval', None) # None is the default value if no interval is specified
    
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()


    # get the CloudStorage settings from the database with scalars
    #settings = db.session.scalars(sa.select(CloudStorage).where(CloudStorage.id == music_id)).first()

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
            #scheduleJobs(music, settings)
            schedule.every(music.interval).minutes.do(download,music_id).tag(music_id)
            print("Interval set for:", music.title, music.interval, "minutes")

    return redirect(url_for("main.musicapp"))

# this function can get the time left before the playlist will be downloaded again
@bp.route("/intervalstatus/<int:music_id>")
@login_required
def intervalStatus(music_id):
    
    time_of_next_run = schedule.next_run(music_id)
    # get current time
    time_now = datetime.datetime.now()
    
    if time_of_next_run is not None:
        # calculate time left before next run
        time_left = time_of_next_run - time_now
        print("Time left before next run:", time_left)
        time_left = time_left.seconds
    else:
        time_left = 0
    
    # return the time left before the next run
    return str(time_left)

@bp.route("/download_history/<int:music_id>")
@login_required
def download_history(music_id):

    # get the download history for the music object, sorted by date added
    musictaskshistory = db.session.scalars(sa.select(MusicTask).where((MusicTask.music_id == music_id) & (MusicTask.user_id == current_user.id)).order_by(MusicTask.timestamp.desc())).all()

    # convert the object to a list of dictionaries
    musictaskshistory_dicts = [musictask.to_dict() for musictask in musictaskshistory]

    # return the dictionaries as a JSON response
    return jsonify(musictaskshistory_dicts)

def scheduletask(music):
    # set actiontype to True, because this is a automated download
    # true is only used for scheduled (or "automated") downloads
    actiontype = True

    # get the user that belongs to the music object
    songowner = db.session.scalars(sa.select(Music).where(Music.id == music.id)).first()
    if songowner:
        username = songowner.musicowner.username
    else: 
        username = None
    
    # get the user object
    # this user object is used to launch the task
    user = db.session.scalars(sa.select(User).where(User.username == username)).first()
    
    # https://github.com/dbader/schedule
    # https://schedule.readthedocs.io/en/stable/
    #schedule.every(music.interval).minutes.do(download_and_upload,music,settings).tag(music.id)
    schedule.every(music.interval).minutes.do(downloadmusicAction,music.id, actiontype, user).tag(music.id)
    print("Interval set for:", music.title, music.interval, "minutes")


def downloadmusicAction(music_id, actiontype, user=None):
    # the user object is supplied by the scheduletask function if it's an automated "scheduled" download
    # if the user is not given, then use the current_user, which is the logged in user
    if user is None and current_user.is_authenticated:
        user = current_user
    
    # get the username for the function
    if user:
        username = user.username

    if user:
        user.launch_task('downloadmusic', 'description123', music_id, actiontype, username)

        # saves the launch task to the database
        db.session.commit()
    else:
        print("No user found, ERROR")


def schedulerbootup():
    # start all the schedulers for the playlists/songs that are monitored
    
    # get the music object from the database with scalars
    music = db.session.scalars(sa.select(Music))

    # check if there are any playlists/songs in the database
    if music is not None:
        # add the schedules for every playlists/songs
        for musics in music:
            #if music.monitored is True and settings is not None:
            if musics.monitored is True:
                print("monitor is ON")
                print("Going to schedule the music to be downloaded on repeat")
                print(musics.monitored)
                # schedule the job   
                scheduletask(musics)