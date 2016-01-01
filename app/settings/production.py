from .common import *

DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path('sqlite3.db')
# SQLALCHEMY_DATABASE_URI = 'postgresql://@localhost:5432/'