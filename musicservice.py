import sqlalchemy as sa
import sqlalchemy.orm as so
from webapp import create_app, db
from webapp.models import User, Music, MusicTask, CloudStorage, WebDavStorage, FTPStorage

webapp = create_app()

@webapp.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Music': Music, 'MusicTask': MusicTask, 'CloudStorage': CloudStorage, 'WebDavStorage': WebDavStorage, 'FTPStorage': FTPStorage}