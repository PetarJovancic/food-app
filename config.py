import os

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')