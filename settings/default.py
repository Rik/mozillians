# -*- coding: utf-8 -*-

# Django settings for the mozillians project.
import logging

from funfactory.manage import path
from funfactory import settings_base as base
from settings import initial as pre

## Log settings
SYSLOG_TAG = "http_app_mozillians"
LOGGING = {
    'loggers': {
        'landing': {'level': logging.INFO},
        'phonebook': {'level': logging.INFO},
    },
}

## L10n
LOCALE_PATHS = [path('locale')]

# Accepted locales
PROD_LANGUAGES = ('de', 'en-US', 'es', 'fr', 'nl', 'pl', 'sl', 'zh-TW')

# List of RTL locales known to this project. Subset of LANGUAGES.
RTL_LANGUAGES = ()  # ('ar', 'fa', 'fa-IR', 'he')

# For absoluate urls
PROTOCOL = "https://"
PORT = 443

## Media and templates.
TEMPLATE_DIRS = base.TEMPLATE_DIRS + (path('apps/users/templates'), )

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ('jingo.Loader',) + base.TEMPLATE_LOADERS

TEMPLATE_CONTEXT_PROCESSORS = (base.TEMPLATE_CONTEXT_PROCESSORS +
    ('django_browserid.context_processors.browserid_form',))


JINGO_EXCLUDE_APPS = [
    'admin',
]

MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/jquery-ui-1.8.16.custom.css',
            'js/libs/tag-it/css/jquery.tagit.css',
            'css/mozilla-base.css',
            'css/main.css',
        ),
    },
    'js': {
        'common': (
            'js/libs/jquery-1.4.4.min.js',
            'js/libs/jquery-ui-1.8.7.custom.min.js',
            'js/libs/tag-it/js/tag-it.js',
            'js/libs/validation/validation.js',
            'js/browserid.js',
            'js/main.js',
            'js/groups.js',
        ),
    }
}

MIDDLEWARE_CLASSES = list(base.MIDDLEWARE_CLASSES) + [
    'commonware.response.middleware.StrictTransportMiddleware',
    'commonware.response.middleware.GraphiteMiddleware',
    'commonware.response.middleware.GraphiteRequestTimingMiddleware',
    'csp.middleware.CSPMiddleware',
    'phonebook.middleware.PermissionDeniedMiddleware',
    'larper.middleware.LarperMiddleware',
]

# StrictTransport
STS_SUBDOMAINS = True

# OpenLDAP
LDAP_USERS_GROUP = 'ou=people,dc=mozillians,dc=org'

# django-auth-ldap
AUTHENTICATION_BACKENDS = (
    'browserid.backend.SaslBrowserIDBackend',
)

INSTALLED_APPS = list(base.INSTALLED_APPS) + [
    'phonebook',
    'users',
    'groups',
    'locations',
    'larper',
    'browserid',

    'csp',
    'django_browserid',  # We use forms, etc. but not the auth backend
    'jingo_minify',
    'tower',
    'cronjobs',

    'django.contrib.admin',
    'django.contrib.auth',

    # DB migrations
    'south',
    # re-assert dominance of 'django_nose'
    'django_nose',

]

## Auth
PWD_ALGORITHM = 'bcrypt'
HMAC_KEYS = {
    '2011-01-01': 'cheesecake',
}

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# BrowserID 21600 would be 6 hour sessions
SESSION_EXP_SECONDS = 21600

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Auth
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

#: Userpics will be uploaded here.
USERPICS_PATH = pre.NETAPP_STORAGE + '/userpics'

#: Userpics will accessed here.
USERPICS_URL = pre.UPLOAD_URL + '/userpics'

AUTH_PROFILE_MODULE = 'users.UserProfile'

MAX_PHOTO_UPLOAD_SIZE = 8 * (1024 ** 2)

AUTO_VOUCH_DOMAINS = ('mozilla.com', 'mozilla.org', 'mozillafoundation.org')
SOUTH_TESTS_MIGRATE = False

# Django-CSP
CSP_IMG_SRC = ("'self'", 'http://statse.webtrendslive.com',
               'https://statse.webtrendslive.com',)
CSP_SCRIPT_SRC = ("'self'", 'http://statse.webtrendslive.com',
                  'https://statse.webtrendslive.com',
                  'http://browserid.org',
                  'https://browserid.org',)
CSP_REPORT_ONLY = True
CSP_REPORT_URI = '/csp/report'
