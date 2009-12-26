from datetime import datetime, timedelta
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from lso.json import json_error, send_json
from lso.util import I18NRequestHandler
from lso.ui import render_write
import config


class SettingsPage(I18NRequestHandler):

  def get(self):

    language = self.request.COOKIES.get('django_language', '')
    style = self.request.COOKIES.get('style', '')
    gravatar_option = self.request.COOKIES.get('gravatar_option', 'identicon')
    name = self.request.COOKIES.get('name', '')
    gravatar = self.request.COOKIES.get('gravatar', '')
    gravatar_check = self.request.COOKIES.get('gravatar_check', '')
    
    tmpl_values = {
        'LANGUAGES': settings.LANGUAGES,
        'language': language,
        'style': style,
        'gravatar_option': gravatar_option,
        'name': name,
        'gravatar': gravatar,
        'gravatar_check': gravatar_check,
        }
    
    render_write(tmpl_values, 'settings.html', self.request, self.response)

  def post(self):

    messages = []

    name = self.request.get('name', '')
    language = self.request.get('language')
    style = self.request.get('style', '')
    gravatar_option = self.request.get('gravatar_option', 'identicon')
    gravatar = self.request.get('gravatar', '')
    gravatar_check = self.request.get('gravatar_check', '')
    if language and language in dict(settings.LANGUAGES).keys():
      self.request.COOKIES['django_language'] = language
      self.reset_language()
    expires = (datetime.utcnow() + timedelta(days=3652)).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
    self.request.COOKIES['style'] = style
    self.request.COOKIES.set_cookie('style', style, max_age=expires)
    self.request.COOKIES.set_cookie('gravatar_option', gravatar_option, max_age=expires)
    Secure = not config.DEV
    self.request.COOKIES.set_cookie('name', name, secure=Secure, max_age=expires)
    self.request.COOKIES.set_cookie('gravatar', gravatar, secure=Secure, max_age=expires)
    self.request.COOKIES.set_cookie('gravatar_check', gravatar_check, secure=Secure, max_age=expires)

    messages.append(('message', _('Settings saved')))
    tmpl_values = {
        'messages': messages,
        'config': config,
        'LANGUAGES': settings.LANGUAGES,
        'language': language,
        'style': style,
        'gravatar_option': gravatar_option,
        'name': name,
        'gravatar': gravatar,
        'gravatar_check': gravatar_check,
        }
    render_write(tmpl_values, 'settings.html', self.request, self.response)

  def head(self):

    pass


application = webapp.WSGIApplication([
    ('/settings', SettingsPage),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
