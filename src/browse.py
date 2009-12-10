import logging
import os
from urllib import unquote

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from lso import rate
from lso.json import json_error, send_json
from lso.models import Secret, Tag
from lso.ui import render_write
from lso.util import I18NRequestHandler
import config
import Simple24 as s24


class SecretPage(I18NRequestHandler):

  def get(self, secret_id):
    
    secret_id = int(secret_id)
    secret = Secret.get_by_id(secret_id)

    template_values = {}

    if secret:
      if secret.hidden:
        self.error(403)
      else:
        template_values['secret'] =  secret
    else:
      self.error(404)

    render_write(template_values, 'secret_page.html', self.request, self.response)

  def head(self, secret_id):

    secret_id = int(secret_id)
    secret = Secret.get_by_id(secret_id)

    if secret:
      if secret.hidden:
        self.error(403)
    else:
      self.error(404)


class FlagJSON(I18NRequestHandler):

  def get(self):

    callback = self.request.get('callback') 
    id = self.request.get('id') 
    if id == '':
      json_error(self.response, _('Invalid Secret ID!'), callback)
      return
    
    secret = Secret.get_by_id(int(id))
    if not secret:
      json_error(self.response, _('Invalid Secret ID!'), callback)
      return
    
    if rate.incr_with_addr('%s' % id, self.request.remote_addr, 1, config.RATE_FLAG_DURATION, 'flag'):
      json_error(self.response, _('You have flagged this secret!'), callback)
      return
    if rate.incr_with_addr('total', self.request.remote_addr, config.RATE_FLAG_MASS, config.RATE_FLAG_MASS_DURATION, 'flag'):
      json_error(self.response, _('You have flagged too many secrets in a short time!'), callback)
      return

    secret.incr_flags()

    send_json(self.response, {'message': _('Flagged'), 'id': id}, callback)


class BrowsePage(I18NRequestHandler):

  def get(self, language, page):

    page = 1 if not page else int(page)

    if language and language == 'all':
      lang_path = 'all/'
      title = _('All')
    elif language:
      if language not in config.DICT_VALID_LANGUAGES:
        self.redirect('/browse')
        return
      lang_path = language + '/'
      title = config.DICT_VALID_LANGUAGES[language]
    else:
      self.redirect('/browse/all')
      return

    q = Secret.all()
    q.filter('hidden =', False)
    if language and language != 'all':
      q.filter('language =', language)
    q.order('-published')
    secrets = q.fetch(10, (page - 1) * 10)

    template_values = {
        'title': title,
        'current_page': page,
        'secrets': secrets,
        'lang_path': lang_path,
        'language': language,
        'cut_story': True,
        'feed_link': '%s/feed/%s' % (self.request.host_url, lang_path),
        }

    if page > 1:
      template_values['prev'] = page - 1
    if page < 100 and len(secrets) == 10 and q.fetch(1, page * 10):
        template_values['next'] = page + 1

    render_write(template_values, 'browse.html', self.request, self.response)

  def head(self, language, page):

    pass


class UserPage(I18NRequestHandler):

  def get(self, hash):

    render_write({}, 'not_implemented.html', self.request, self.response)


class TagCloudPage(I18NRequestHandler):

  def get(self, language):

    if language and language == 'all':
      #lang_path = 'all/'
      #title = _('All')
      render_write({}, 'not_implemented.html', self.request, self.response)
      return
    elif language:
      if language not in config.DICT_VALID_LANGUAGES:
        self.redirect('/browse')
        return
      lang_path = language + '/'
      title = config.DICT_VALID_LANGUAGES[language]
    else:
      self.redirect('/browse/all')
      return

    q = Tag.all()
    if language and language != 'all':
      q.filter('language =', language)
    q.order('-count')
    tags = q.fetch(100)
    if tags:
      max_count = tags[0].count
      # Sort by tag name
      tags.sort(lambda x, y: cmp(x.name.lower(), y.name.lower()))
      new_tags = []
      for tag in tags:
        new_tags.append({'name': tag.name.encode('utf-8'), 'count': tag.count, 'size': 1.0 + 1.0 * tag.count / max_count})
      tags = new_tags

    template_values = {
        'title': title,
        'tags': tags,
        'lang_path': lang_path,
        'language': language,
        'feed_link': '%s/feed/%s' % (self.request.host_url, lang_path),
        }

    render_write(template_values, 'tagcloud.html', self.request, self.response)

  def head(self, language, page):

    pass


class TagPage(I18NRequestHandler):

  def get(self, language, tag, page):

    page = 1 if not page else int(page)
    tag = unquote(tag).decode('utf-8')
    if language and language == 'all':
      lang_path = 'all/'
      title = _('All')
    elif language:
      if language not in config.DICT_VALID_LANGUAGES:
        self.redirect('/browse')
        return
      lang_path = language + '/'
      title = config.DICT_VALID_LANGUAGES[language]
    else:
      self.redirect('/browse/all')
      return

    q = Secret.all()
    q.filter('hidden =', False)
    if language and language != 'all':
      q.filter('language =', language)
    q.filter('tags IN', [tag])
    q.order('-published')
    secrets = q.fetch(10, (page - 1) * 10)

    template_values = {
        'title': title,
        'tag': tag.encode('utf-8'),
        'current_page': page,
        'secrets': secrets,
        'lang_path': lang_path,
        'language': language,
        'cut_story': True,
        'feed_link': '%s/feed/%s' % (self.request.host_url, lang_path),
        }

    if page > 1:
      template_values['prev'] = page - 1
    if page < 100 and len(secrets) == 10 and q.fetch(1, page * 10):
        template_values['next'] = page + 1

    render_write(template_values, 'browse.html', self.request, self.response)

  def head(self, language, page):

    pass


application = webapp.WSGIApplication([
    (r'/(\d+)', SecretPage),
    (r'/flag\.json', FlagJSON),
    ('/u/(.*)', UserPage),
    ('/browse/?([a-zA-Z_]*)/?([0-9]*)/?', BrowsePage),
    ('/tag/([a-zA-Z_]+)/?', TagCloudPage),
    ('/tag/([a-zA-Z_]+)/([^/]+)/?([0-9]*)/?', TagPage),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
