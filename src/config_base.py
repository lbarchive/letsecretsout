# -*- coding: utf-8 -*-

import os

# Switches
DEBUG = True
DISQUS_ENABLED = False
reCAPTCHA_ENABLED = False

DEFAULT_STYLE = 'dark'
DEFAULT_GRAVATAR = 'identicon'

# reCAPTCHA
reCAPTCHA_PUBLIC_KEY = ''
reCAPTCHA_PRIVATE_KEY = ''

SECRET_NAME_MINLENGTH = 2
SECRET_NAME_MAXLENGTH = 50
SECRET_SUBJECT_MINLENGTH = {
    'default': 5,
    'en': 20,
    'es': 20,
    'fr': 20,
    }
SECRET_SUBJECT_MAXLENGTH = 100
SECRET_STORY_MINLENGTH = {
    'default': 20,
    'en': 100,
    'es': 100,
    'fr': 100,
    }
SECRET_STORY_MAXLENGTH = 4000
SECRET_MAX_TAGS = 10
SECRET_TAG_MAXLENGTH = 50

SECRET_FLAGS_TO_HIDE = 20

FEED_ITEMS = 20
FEED_CACHE = 60 * 10

# Rate limit
RATE_POST_DURATION = 600
RATE_FLAG_DURATION = 3600
RATE_FLAG_MASS = 5
RATE_FLAG_MASS_DURATION = 60

# For being used for hashing, salt should be look like a strong password.
SALT = r''
GRAVATAR_CHECK_SALT = r''

# Valid language to submit
VALID_LANGUAGES = (
    # 'en', 'zh_TW' should match the directories in conf/locale/*
#    ('de', 'Deutsch'),
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
#    ('it', 'Italiano'),
    ('ja', '日本語'),
#    ('ko', '한국어'),
#    ('pt', 'Português'),
    ('zh_CN', '简体中文'),
    ('zh_TW', '繁體中文'),
    )
DICT_VALID_LANGUAGES = dict(VALID_LANGUAGES)
KEYS_VALID_LANGUAGES = DICT_VALID_LANGUAGES.keys()

# Valid styles
VALID_STYLES = (
    ('light', _('Light')),
    ('dark', _('Dark')),
    )
DICT_VALID_STYLES = dict(VALID_STYLES)
KEYS_VALID_STYLES = DICT_VALID_STYLES.keys()

# Valid Gravtar avatar options
VALID_GRA_OPTIONS = (
    ('gravatar', _('Gravatar')),
    ('secret', _('Secret')),
    ('identicon', _('Identicon')),
    ('monsterid', _('MonsterID')),
    ('wavatar', _('Wavatars')),
    ('off', _('Turn off Gravatar')),
    )
DICT_VALID_GRA_OPTIONS = dict(VALID_GRA_OPTIONS)
KEYS_VALID_GRA_OPTIONS = DICT_VALID_GRA_OPTIONS.keys()

# Under development server?
DEV = os.environ['SERVER_SOFTWARE'].startswith('Development')

# Base URI
if DEV:
  BASE_URI = 'http://localhost:8080/'
  BASE_SECURE_URI = BASE_URI
else:
  BASE_URI = 'http://%s.appspot.com/' % os.environ['APPLICATION_ID']
  BASE_SECURE_URI = 'https://%s.appspot.com/' % os.environ['APPLICATION_ID']

BEFORE_HEAD_END = ''
BEFORE_BODY_END = ''
