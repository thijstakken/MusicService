import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # /// = relative path, //// = absolute path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'webapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b'/\xed\xb4\x87$E\xf4O\xbb\x8fpb\xad\xc2\x88\x90!\x89\x18\xd0z\x15~Z'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'