from db import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    mobile = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(100), nullable=True, default=None)

    def __repr__(self):
        return f"user {self.username}"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    events = db.relationship('Event', backref='category', lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    long_description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Float, nullable=False, default=0.0)
    organizer = db.Column(db.String(100), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('events', lazy=True)) # ივენთის ავტორის სახელს ინახავს ამ ცვლადში 

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# UserMixin  კლასი flask_login ში. აქვს 4 თვისება:
# is_authenticated, is_active, is_anonymous, get_id()