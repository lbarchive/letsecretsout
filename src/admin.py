import logging as log
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from lso.json import json_error, send_json
from lso.models import Secret, Tag
from lso.ui import render_write
from lso.util import I18NRequestHandler
import config


class AdminPage(I18NRequestHandler):

  def get(self):
 
    q = Secret.all()
#    q.filter('hidden =', True)
    q.filter('flags >', 0)
    q.order('-flags')
    secrets = q.fetch(10)
#    for secret in secrets:
#      # Has to make sure variables in {% blocktrans %} is type str, or this
#      # error:
#      # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 1: ordinal not in range(128)
#      secret.name = secret.name.encode('utf-8')

    tmpl_values = {
        'config': config,
        'is_admin': True,
        'secrets': secrets,
        }
    render_write(tmpl_values, 'admin.html', self.request, self.response)

  def head(self):

    pass


class DeleteJSON(I18NRequestHandler):

  def get(self):

    callback = self.request.get('callback') 
    id = self.request.get('id') 
    if id == '':
      json_error(self.response, 'Invalid Secret ID', callback)
      return
    
    # Must log in
    if not users.is_current_user_admin():
      json_error(self.respoonse, 'Admin login required', callback)
      return

    secret = Secret.get_by_id(int(id))
    if not secret:
      json_error(self.response, 'Invalid Secret ID', callback)
      return

    # Begin to delete
#    Counter('secret').increment(-1)
#    Counter('secret_%s' % thx.language).increment(-1)
    # Remove tags
    key_names = ['%s_%s' % (secret.language, tag) for tag in secret.tags]
    tags = Tag.get_by_key_name(key_names)
    if tags:
      for tag in tags:
        if tag.count:
          tag.count = tag.count - 1
      db.put(tags)
    secret.delete()

    send_json(self.response, {'message': _('Deleted'), 'id': id}, callback)


application = webapp.WSGIApplication([
    ('/admin/?', AdminPage),
    (r'/admin/delete\.json', DeleteJSON),
    ],
    debug=config.DEBUG)


def main():
  """Main function"""
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
