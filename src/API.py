import logging as log
import os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None
from django.utils import feedgenerator

from lso.models import Secret
from lso.util import I18NRequestHandler
import config
import Simple24 as s24


class Feed(I18NRequestHandler):

  def get(self, language, tag):
 
    if not language:
      # TODO respond 404
      self.error(404)
      return
    if language in config.DICT_VALID_LANGUAGES:
#    if language not in config.DICT_VALID_LANGUAGES:
#        log.warning('Invalid language: %s' % language)
#        self.error(500)
#        self.response.out.write('Invalid language: %s' % language)
#        return
      mem_key = 'feed_%s_%s' % (language, tag)
      feed_url = '%sfeed/%s/%s' % (config.BASE_URI, language, tag)
    elif language == 'all':
      mem_key = 'feed_all_%s' % tag
      feed_url = '%sfeed/all/%s' % (config.BASE_URI, tag)
    else:
      # TODO 404
      self.error(404)
      return

    raw_feed = memcache.get(mem_key)
    if raw_feed:
      self.response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
      self.response.out.write(raw_feed)
      return

    feed = feedgenerator.Rss201rev2Feed(
        title=_('Let Secrets Out'), # FIXME need language and tag
        link=config.BASE_URI,
        description=_('A place to talk about your secrets.'),
        feed_url=feed_url,
        )
    
    query = Secret.all()
    if language != 'all':
      feed.language = language
      query.filter('language =', language)
    if tag:
      query.filter('tags IN', [tag])
    query.order('-published')

    secrets = query.fetch(config.FEED_ITEMS)
    for secret in secrets:
      feed.add_item(
          title=template.Template('{{ subject }}').render(template.Context({'subject': secret.subject})),
          link='%s%d' % (config.BASE_URI, secret.key().id()),
          description=template.Template('{{ story|linebreaks }}').render(template.Context({'story': secret.story})),
          author_name=template.Template('{{ name }}').render(template.Context({'name': secret.name})),
          author_email='noreply@letsecretsout.appspot.com',
          pubdate=secret.published, unique_id='%s%d' % (config.BASE_URI, secret.key().id()),
          categories=secret.tags,
          )

    raw_feed = feed.writeString('utf-8')
    self.response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    self.response.out.write(raw_feed)
    
    # Cache it
    if not memcache.set(mem_key, raw_feed, config.FEED_CACHE):
      log.error('Unable to cache %s' % mem_key)

    # Simple24
    s24.incr('feed')
    s24.incr(mem_key)


application = webapp.WSGIApplication([
    ('/feed/?([a-zA-Z_]*)/?([^/]*)/?', Feed),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
