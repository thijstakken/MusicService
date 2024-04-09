from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
import sqlalchemy as sa
from webapp import db
# from webapp.main.forms import MusicForm, CloudStorageForm ???
from webapp.models import Music, CloudStorage
from webapp.main import bp

import schedule
from webapp.downloadScheduler import scheduleJobs, deleteJobs, immediateJob, run_schedule
from webapp.main.forms import MusicForm

@bp.route("/", methods=["GET", "POST"])
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
        return redirect(url_for('main.musicapp'))

    return render_template("musicapp.html", music_list=music_list, form=form)
    #return "musicapppage"

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
    music = db.session.scalars(sa.select(Music).where(Music.id == music_id)).first()
    # execute the download function to download one time
    if music is not None and settings is not None:
        immediateJob(music, settings)
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

    return redirect(url_for("main.musicapp"))

# this function can get the time left before the playlist will be downloaded again
@bp.route("/intervalstatus/<int:music_id>")
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