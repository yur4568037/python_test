from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length

class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    access = IntegerField('Access', validators=[DataRequired()])
    #description = StringField('Description', validators=[DataRequired()])
    #description = TextAreaField('Description', validators=[Length(max=200)])
    description = TextAreaField('Description')
    password = PasswordField('Password', validators=[DataRequired()])

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    access = StringField('Access', validators=[DataRequired()])
    userpass = PasswordField('Password', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    

    