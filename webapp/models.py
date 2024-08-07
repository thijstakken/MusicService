from typing import Optional
import sqlalchemy as sa # general sqlalchemy functions
import sqlalchemy.orm as so # supports the use of models
from werkzeug.security import generate_password_hash, check_password_hash
from webapp import db
from flask_login import UserMixin
from webapp import login
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
import redis
import rq
import redis.exceptions
import rq.exceptions
from flask import current_app
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    def set_password(self, password):
        # sets the password for the user
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # returns True if password is correct
        return check_password_hash(self.password_hash, password)

    musics: so.WriteOnlyMapped['Music'] = so.relationship(back_populates='musicowner')
    cloud_storages: so.WriteOnlyMapped['CloudStorage'] = so.relationship(back_populates='storageowner')
    # links the download tasks to the corrosponding playlist/music
    musictasks: so.WriteOnlyMapped['MusicTask'] = so.relationship(back_populates='downloadmusictask')

    def launch_task(self, name, description, musicid, actiontype, username, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(f'webapp.tasks.{name}', musicid, username,
                                                *args, **kwargs)
        task = MusicTask(id=rq_job.get_id(), name=name, description=description, downloadmusictask=self, music_id=musicid, actiontype=actiontype)

        #task = MusicTask
        #task.id = rq_job.get_id()
        #task.name = name
        #task.description = description
        
        #task.playlist = self
        #task.url = music.url
        #task.music_id = music.id
        
        #task.downloadmusictask = self
        db.session.add(task)
        return task
    
    def get_tasks_in_progress(self):
       query = self.musictasks.select().where(MusicTask.complete == False)
       return db.session.scalars(query)

    def get_task_in_progress(self, name):
       query = self.musictasks.select().where(MusicTask.name == name,
                                         MusicTask.complete == False)
       return db.session.scalar(query)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Music(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # we want to couple the music settings to a user account
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    url: so.Mapped[str] = so.mapped_column(sa.String(200))
    monitored: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    interval: so.Mapped[int] = so.mapped_column(sa.Integer)

    musicowner: so.Mapped[User] = so.relationship(back_populates='musics')
    #tasks = so.relationship('MusicTask', backref='music')

    def __repr__(self):
        return '<Music {}>'.format(self.title)
    

class MusicTask(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(36), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    complete: so.Mapped[bool] = so.mapped_column(default=False)
    music_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    actiontype: so.Mapped[bool] = so.mapped_column(sa.Boolean)

    downloadmusictask: so.Mapped[User] = so.relationship(back_populates='musictasks')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# all classes related to CloudStorage are built on a polymorphic relationship
# this will have CloudStorage as a base model
# and WebDavStorage and FTPStorage etc. as subclasses
# this will allows us to have a single table for all cloud storage settings
# and we can use the protocol_type to determine which subclass to use
# which makes it easier to add more protocols in the future

# the following code is based on the example from the sqlalchemy documentation
# https://docs.sqlalchemy.org/en/20/orm/inheritance.html

# check out how to query the database with polymorphic relationships here
# https://docs.sqlalchemy.org/en/20/orm/queryguide/inheritance.html
    
class CloudStorage(db.Model):
    __tablename__ = 'cloud_storage'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # we want to couple the WebDAV settings to a user account
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    # we want to be able to know which protocol to use
    protocol_type: so.Mapped[str] = so.mapped_column(sa.String(30))
    
    storageowner: so.Mapped[User] = so.relationship(back_populates='cloud_storages')

    __mapper_args__ = {
        'polymorphic_identity':'cloud_storage',
        'polymorphic_on':'protocol_type',
    }

    def __repr__(self):
        return '<CloudStorage {}>'.format(self.protocol_type)
    
class WebDavStorage(CloudStorage):
    __tablename__ = 'webdav_storage'
    id: so.Mapped[int] = so.mapped_column(ForeignKey("cloud_storage.id"), primary_key=True)
    # we want to be able to know which protocol to use
    url: so.Mapped[str] = so.mapped_column(sa.String(250))
    directory: so.Mapped[str] = so.mapped_column(sa.String(250))
    username: so.Mapped[str] = so.mapped_column(sa.String(30))
    password: so.Mapped[str] = so.mapped_column(sa.String(100))

    __mapper_args__ = {
        'polymorphic_identity':'webdav_storage',
    }

    def __repr__(self):
        return '<WebDavStorage {}>'.format(self.url)
    
class LocalStorage(CloudStorage):
    __tablename__ = 'local_storage'
    id: so.Mapped[int] = so.mapped_column(ForeignKey("cloud_storage.id"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'local_storage',
    }

    def __repr__(self):
        return '<CloudStorage {}>'.format(self.protocol_type)

class FTPStorage(CloudStorage):
    __tablename__ = 'ftp_storage'
    id: so.Mapped[int] = so.mapped_column(ForeignKey("cloud_storage.id"), primary_key=True)
    host: so.Mapped[str] = so.mapped_column(sa.String(250))
    port: so.Mapped[int] = so.mapped_column(sa.Integer)
    username: so.Mapped[str] = so.mapped_column(sa.String(30))
    password: so.Mapped[str] = so.mapped_column(sa.String(100))

    __mapper_args__ = {
        'polymorphic_identity':'ftp_storage',
    }

    def __repr__(self):
        return '<CloudStorage {}>'.format(self.host)


# Add more classes as needed for other protocols 