from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, URL
    

class WebDAV(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    directory = StringField('Directory', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add WebDAV account')