from os import getenv
from os import environ
import os
import dj_database_url

# Django settings for future project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

if not environ.has_key('FUTURE_DIR'):
    # we're on heroku
    HEROKU_PROJECT_DIR = os.path.dirname(__file__)
else:
    HEROKU_PROJECT_DIR = None 


DATABASES = {}

if not HEROKU_PROJECT_DIR:
    #this is local

    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': getenv('FUTURE_DIR') + 'future/futuredb',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }
else:
    DATABASES['default'] =  dj_database_url.config()


#url = urlparse(environ['DATABASE_URL'])
    
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.postgresql_psycopg2',
#     'NAME': url.path[1:],
#     'USER': url.username,
#     'PASSWORD': url.password,
#     'HOST': url.hostname,
#     'PORT': url.port,
#     }    

# Settings for facebook authentication with our own Authentication
FACEBOOK_APP_ID              = getenv('FUTURE_FB_KEY')
FACEBOOK_API_SECRET          = getenv('FUTURE_FB_SECRET')
#if getenv('FUTURE_ENVIRONMENT') == 'production':
if HEROKU_PROJECT_DIR:
    #BASE_URI = 'http://webfsite.herokuapp.com/'
    BASE_URI = 'http://frozen-caverns-1324.herokuapp.com/'
else:
    BASE_URI                     = 'http://localhost:5000/'

# Setup outgoing email settings
EMAIL_USER_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'webfsite@gmail.com'
EMAIL_HOST_PASSWORD = getenv('FUTURE_EMAIL_PASS')
EMAIL_PORT = 587

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

if not HEROKU_PROJECT_DIR:
    # local:
    # Absolute filesystem path to the directory that will hold user-uploaded files.
    # Example: "/home/media/media.lawrence.com/media/"
    MEDIA_ROOT = getenv('FUTURE_DIR') + 'future/static/'
else:
    MEDIA_ROOT = os.path.join(HEROKU_PROJECT_DIR, "templates")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = '/static/'
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
if not HEROKU_PROJECT_DIR:
    # STATIC_ROOT = ''
    # # List of finder classes that know how to find static files in
    # # various locations.
    # STATICFILES_FINDERS = (
    #     'django.contrib.staticfiles.finders.FileSystemFinder',
    #     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # )
    # STATICFILES_DIRS = (
    #     getenv('FUTURE_DIR') + 'future/static/',
    # )
    # # URL prefix for static files.
    # # Example: "http://media.lawrence.com/static/"
    # STATIC_URL = '/static/'

    # STATIC_ROOT = ''

    # URL prefix for static files.
    # Example: "http://media.lawrence.com/static/"
    STATIC_URL = '/static/'

    # List of finder classes that know how to find static files in
    # various locations.
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

else:
    STATIC_ROOT = os.path.join(HEROKU_PROJECT_DIR, 'static')
    #STATIC_ROOT = 'staticfiles'
    STATICFILES_DIRS = (
        os.path.join(HEROKU_PROJECT_DIR, 'static'),
    )
    STATIC_URL = os.path.join(HEROKU_PROJECT_DIR, 'static')


# # List of finder classes that know how to find static files in
# # various locations.
# STATICFILES_FINDERS = (
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# )

# Make this unique, and don't share it with anybody.
SECRET_KEY = getenv('FUTURE_PYTHON_SECRET')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'future.urls'

if not HEROKU_PROJECT_DIR:
    TEMPLATE_DIRS = (
        getenv('FUTURE_DIR') + 'future/templates',
    )
else:
    TEMPLATE_DIRS = (
        os.path.join(HEROKU_PROJECT_DIR, 'templates'),
    )

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gunicorn',
    'future.futureapp',
)
