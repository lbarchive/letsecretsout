USE_I18N = True

# Valid languages
LANGUAGES = (
    # 'en', 'zh_TW' should match the directories in conf/locale/*
    ('en-us', _('US English')),
    ('zh-tw', _('Traditional Chinese')),
    )

# This is a default language
LANGUAGE_CODE = 'en-us'

# Custom template tags
INSTALLED_APPS = (
    'lso',
    )
