from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeLocalField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile = StringField('Mobile', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose a different one.')
        
    def validate_username(self, username):  
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')



class EventForm(FlaskForm):
    title = StringField('სათაური', validators=[DataRequired()])
    short_description = StringField('მოკლე აღწერა', validators=[DataRequired(), Length(max=200)])
    long_description = TextAreaField('სრული აღწერა', validators=[DataRequired()])
    location = StringField('ლოკაცია (ქალაქი)', validators=[DataRequired()])
    event_date = DateTimeLocalField('ჩატარების თარიღი', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    price = FloatField('ბილეთის ფასი (₾)', validators=[DataRequired()])
    organizer = StringField('ორგანიზატორი', validators=[DataRequired()])
    category_id = SelectField('კატეგორია', coerce=int, validators=[DataRequired()])
    submit = SubmitField('შენახვა')



class UpdateProfileForm(FlaskForm):
    username = StringField('მომხმარებელი', validators=[DataRequired()])
    email = StringField('ელ-ფოსტა', validators=[DataRequired(), Email()])
    picture = FileField('პროფილის სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('განახლება')

    def validate_email(self, email):
        if email.data != current_user.email:     # თუ მომხმარებელს შეყავს ახალი იმეილი, ჯერ ვამოწმებთ ბაზაში არსებობს თუ არა ასეთი იმეილი, თუ არსებობს ვუჩვენებთ ერორს. 
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('იმეილი უკვე არსებობს, ხელახლა სცადეთ')
        
    def validate_username(self, username):  
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('ასეთი ზედმეტსახელი უკვე არსებობს, სცადეთ თავიდან.')