from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email
from flask_wtf.file import FileField, FileAllowed, FileRequired

class loginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

class registerForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    age = StringField('Age', validators=[InputRequired()])
    image = FileField('DP', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])

class wishlistForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = StringField('Description', validators=[InputRequired()])
    url = StringField('Website', validators=[InputRequired()])
    thumbnail = StringField('Thumbnail', validators=[InputRequired()])

class shareForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')
