from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, EqualTo, URL
import sqlalchemy as sa
from webapp import db
from webapp.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')
        
class MusicForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    # set monitored to false by default
    monitored = BooleanField('Monitored', default=False)
    # set interval to integer 10 by default
    interval = IntegerField('Interval', default=10)

    #user_id = db.relationship(User, back_populates='musics')

    #user_id = 1

    submit = SubmitField('Add Music')

class CloudStorageForm(FlaskForm):
    protocol = StringField('Protocol', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    directory = StringField('Directory', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add Cloud Storage')