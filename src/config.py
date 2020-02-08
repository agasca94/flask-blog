import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

UPLOAD_FOLDER = './src/static/'
TEST_UPLOAD_FOLDER = './src/static/testing/'


class Development(object):
    DEBUG = True
    TESTING = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_FOLDER = UPLOAD_FOLDER


class Production(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=45)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_FOLDER = UPLOAD_FOLDER


class Testing(object):
    TESTING = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_FOLDER = TEST_UPLOAD_FOLDER


app_config = {
    'development': Development,
    'production': Production,
    'testing': Testing
}
