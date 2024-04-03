from webapp import app

import sqlalchemy as sa
import sqlalchemy.orm as so
from webapp import db
from webapp.models import User, Music, MusicTask

webapp = app

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Music': Music, 'MusicTask': MusicTask}
