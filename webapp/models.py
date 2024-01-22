from typing import Optional
import sqlalchemy as sa # general sqlalchemy functions
import sqlalchemy.orm as so # supports the use of models
from webapp import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    #email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)


#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(64))
#    password_hash = db.Column(db.String(128))
    #email = db.Column(db.String(100), unique=True)


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # we want to couple the music settings to a user account
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    monitored = db.Column(db.Boolean)
    interval = db.Column(db.Integer)

class WebDAV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # we want to couple the WebDAV settings to a user account
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    WebDAV_URL = db.Column(db.String(250))
    WebDAV_Directory = db.Column(db.String(250))
    WebDAV_Username = db.Column(db.String(30))
    WebDAV_Password = db.Column(db.String(100))