import os
from dotenv import load_dotenv

load_dotenv()    # .env ფაილიდან მოაქვს ინფორმაცია

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///events.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')