import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///diet_analyzer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID')
    NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY')