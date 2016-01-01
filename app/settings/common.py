# -*- coding: utf-8 -*-
import os
from flask.ext.babelex import lazy_gettext, gettext as _, ngettext
import babel, pytz
from datetime import datetime, timedelta

def path(*args):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', *args))

SECRET_KEY = '\x8f\xb2KTt\xd0\xe7\xf1"\xd2\x86:\xb9\xdcF\xf1\x18\x1c\x92\xb6\xbbk\xa0\x02'

SITE_NAME = 'Migom'

BABEL_DEFAULT_LOCALE = 'ru'

BABEL_DEFAULT_TIMEZONE = 'UTC'

RECAPTCHA_USE_SSL = True

RECAPTCHA_PUBLIC_KEY = '6LfGxuYSAAAAAB5OZkdl9LZu84h4RBuRNRpaLOBu'

RECAPTCHA_PRIVATE_KEY = '6LfGxuYSAAAAAO2TQK2EJcAUtbJHyEu0Ge9YNSVf'

LANGUAGES = [('en', u'English'), ('ru', u'Русский')]

RANKS = [(1, _(u'Driver'), 3), (2, _(u'Operator'), 3), (3, _(u'Manager'), 4), (4, _(u'Senior Manager'), 5)]

IMAGES = ['png', 'jpg', 'jpeg']

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

UPLOADS_FOLDER = path('media')

MEDIA_FOLDER = path('media')

MEDIA_URL = '/media/'

MEDIA_THUMBNAIL_FOLDER = path('media/cache')

MEDIA_THUMBNAIL_URL = '/media/cache/'

ACTIVE_DRIVER_TIMEDELTA = timedelta(seconds=10)

MAIL_SERVER = 'smtp.gmail.com'

MAIL_PORT = 465

MAIL_USE_TLS = False

MAIL_USE_SSL = True

MAIL_USERNAME = 'sibiryakov.ya@gmail.com'

MAIL_PASSWORD = '1409199696Rus'

SITE_URL = 'http://188.225.32.169/'

RQ_DEFAULT_HOST = 'localhost'

RQ_DEFAULT_PORT = 6479

RQ_DEFAULT_PASSWORD = 2748

RQ_DEFAULT_DB = 0

CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'