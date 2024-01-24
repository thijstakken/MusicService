from typing import Optional
import sqlalchemy as sa # general sqlalchemy functions
import sqlalchemy.orm as so # supports the use of models
from webapp import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    #email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)

    musics: so.WriteOnlyMapped['Music'] = so.relationship(back_populates='owner')
    cloud_storages: so.WriteOnlyMapped['CloudStorage'] = so.relationship(back_populates='owner')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Music(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # we want to couple the music settings to a user account
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    url: so.Mapped[str] = so.mapped_column(sa.String(200))
    monitored: so.Mapped[bool] = so.mapped_column(sa.Boolean)
    interval: so.Mapped[int] = so.mapped_column(sa.Integer)

    owner: so.Mapped[User] = so.relationship(back_populates='musics')

    def __repr__(self):
        return '<Music {}>'.format(self.title)

class CloudStorage(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # we want to couple the WebDAV settings to a user account
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    # we want to be able to know which protocol to use
    protocol: so.Mapped[str] = so.mapped_column(sa.String(15))
    url: so.Mapped[str] = so.mapped_column(sa.String(250))
    directory: so.Mapped[str] = so.mapped_column(sa.String(250))
    username: so.Mapped[str] = so.mapped_column(sa.String(30))
    password: so.Mapped[str] = so.mapped_column(sa.String(100))

    owner: so.Mapped[User] = so.relationship(back_populates='cloud_storages')

    def __repr__(self):
        return '<CloudStorage {}>'.format(self.url)
    

# this below is an possible implementation of a polymorphic relationship
# this will have CloudStorage as a base model
# and WebDavStorage and FTPStorage as subclasses
# this will allow us to have a single table for all cloud storage settings
# and we can use the protocol_type to determine which subclass to use
# which makes it easier to add more protocols in the future
"""
class CloudStorage(db.Model):
    __tablename__ = 'cloud_storage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    protocol_type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity':'cloud_storage',
        'polymorphic_on':protocol_type
    }

class WebDavStorage(CloudStorage):
    __tablename__ = 'webdav_storage'
    id = db.Column(db.Integer, db.ForeignKey('cloud_storage.id'), primary_key=True)
    url = db.Column(db.String(250))
    directory = db.Column(db.String(250))
    username = db.Column(db.String(30))
    password = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity':'webdav_storage',
    }

class FTPStorage(CloudStorage):
    __tablename__ = 'ftp_storage'
    id = db.Column(db.Integer, db.ForeignKey('cloud_storage.id'), primary_key=True)
    host = db.Column(db.String(250))
    port = db.Column(db.Integer)
    username = db.Column(db.String(30))
    password = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity':'ftp_storage',
    }

# Add more classes as needed for other protocols """