
import logging
import re
import os

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from lso import rate
from lso.json import json_error, send_json
from lso.models import Secret
from lso.util import I18NRequestHandler, is_email, get_gravatar, get_gravatar_check, verify_reCAPTCHA
from lso.ui import render_write
import config
import Simple24 as s24


class PostPage(I18NRequestHandler):

  def get(self):

    name = self.request.COOKIES.get('name', '')
    gravatar = self.request.COOKIES.get('gravatar', '')
    gravatar_check = self.request.COOKIES.get('gravatar_check', '')

    tmpl_values = {
        'name': name,
        'gravatar': gravatar,
        'gravatar_check': gravatar_check,
        'subject': '',
        'story': '',
        }
    render_write(tmpl_values, 'post.html', self.request, self.response)

  def post(self):

    # Get values
    name = self.request.get('name')
    gravatar = self.request.get('gravatar')
    gravatar_check = self.request.get('gravatar_check')
    language = self.request.get('language')
    subject = self.request.get('subject')
    tags = self.request.get('tags')
    story = self.request.get('story')
    if config.reCAPTCHA_ENABLED:
      recaptcha_challenge = self.request.get('recaptcha_challenge_field')
      recaptcha_response = self.request.get('recaptcha_response_field')

    try:
      secret = Secret(name=name, language=language, subject=subject, story=story)
      secret.prepare_put(tags, gravatar, gravatar_check)
      # Check reCAPTCHA
      if config.reCAPTCHA_ENABLED:
        if not recaptcha_response:
          raise ValueError(_('You need to enter the reCAPTCHA words!'))
        if not verify_reCAPTCHA(self.request.remote_addr, recaptcha_challenge, recaptcha_response):
          # TODO incorrect words may not be only reason to fail
          raise ValueError(_('You did not enter the correct reCAPTCHA wrods, please try again!'))

      if rate.incr_with_addr('count', self.request.remote_addr, 1, config.RATE_POST_DURATION, 'post'):
        # FIXME you should not be this lazy!
        raise ValueError(_('You have posted too many secrets in a short time!'))
      
      secret.put()
      secret.post_put()
      
      s24.incr('new_secrets')
      self.redirect('/%d' % secret.key().id())

    except ValueError, e:
      tmpl_values = {
          'messages': (('error', e.message), ),
          'name': name,
          'gravatar': gravatar,
          'gravatar_check': gravatar_check,
          'language': language,
          'subject' : subject,
          'story': story,
          'tags': tags,
          }
      render_write(tmpl_values, 'post.html', self.request, self.response)
    except db.BadValueError, e:
      # TODO
      m = re.match('Property (\w+) is required', e.message)
      if not m:
        raise e
      d = {'subject': _('Subject'), 'story': _('Story')}
      field_name = d.get(m.group(1), m.group(1))
      tmpl_values = {
          'messages': (('error', _('%s is required') % field_name), ),
          'name': name,
          'gravatar': gravatar,
          'gravatar_check': gravatar_check,
          'language': language,
          'subject' : subject,
          'story': story,
          'tags': tags,
          }
      render_write(tmpl_values, 'post.html', self.request, self.response)

  def head(self):

    pass


class PreviewJSON(I18NRequestHandler):

  def post(self):
    
    # Get values
    name = self.request.get('name')
    gravatar = self.request.get('gravatar')
    gravatar_check = self.request.get('gravatar_check')
    language = self.request.get('language')
    subject = self.request.get('subject')
    story = self.request.get('story')
    tags = self.request.get('tags')
    callback = self.request.get('callback') 

    try:
      secret = Secret(name=name, language=language, subject=subject, story=story)
      secret.prepare_put(tags, gravatar, gravatar_check)
      tmpl_values = {
          'secret': secret,
          }
      send_json(self.response, {'preview_header': _('Preview of Your Secret'),
          'secret_preview': render_write(tmpl_values, 'secret_item.html')}, callback)
    except ValueError, e:
      json_error(self.response, e.message, callback)
    except db.BadValueError, e:
      # TODO
      m = re.match('Property (\w+) is required', e.message)
      if not m:
        raise e
      d = {'subject': _('Subject'), 'story': _('Story')}
      field_name = d.get(m.group(1), m.group(1))
      json_error(self.response, _('%s is required') % field_name, callback)


class SendGravatarCheckJSON(I18NRequestHandler):

  def post(self):
    
    # Get values
    gravatar = self.request.get('gravatar')
    callback = self.request.get('callback') 
    if not is_email(gravatar):
      json_error(self.response, _('You have to enter an email address in Gravatar field!'), callback)
      return
    gravatar_check = get_gravatar_check(get_gravatar(gravatar.lower()))
    mail.send_mail(sender='Let Secrets Out <noreply@letsecretsout.appspotmail.com>',
        to=gravatar, subject=_('You Gravatar Check for Let Secrets Out'),
        body=_('The Gravatar Check for %(gravatar)s is %(gravatar_check)s') % {'gravatar': gravatar, 'gravatar_check': gravatar_check})
    send_json(self.response, {'message': _('The Gravatar Check has been sent to %s, please check your mailbox.') % gravatar}, callback)

application = webapp.WSGIApplication([
    ('/post', PostPage),
    (r'/preview\.json', PreviewJSON),
    (r'/send_gravatar_check\.json', SendGravatarCheckJSON),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
