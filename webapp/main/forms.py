from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, URL


class MusicForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    # set monitored to false by default
    monitored = BooleanField('Monitored', default=False)
    # set interval to integer 10 by default
    interval = IntegerField('Interval', default=10)
    submit = SubmitField('Add Music')