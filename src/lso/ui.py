import os
import urllib

from google.appengine.ext.webapp import template

import config


def render_write(tmpl_values, tmpl_name, request=None, response=None):
  # A helper function to set up some common stuff, render, then write to client
  if 'HEAD' not in tmpl_values:
    tmpl_values['HEAD'] = ''
  tmpl_values['HEAD'] += '  <link href="/css/main.css?r=7" type="text/css" rel="stylesheet"/>\n'
  tmpl_values['HEAD'] += '  <script src="http://www.google.com/jsapi" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <script src="/js/main.js?r=1" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <script src="/js/jquery.easing.js" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <script src="/js/humanmsg.js" type="text/javascript"></script>\n'
  tmpl_values['HEAD'] += '  <link href="/css/humanmsg.css" type="text/css" rel="stylesheet"/>\n'
  if request:
    style = request.COOKIES.get('style', '')
    if style and style in config.KEYS_VALID_STYLES:
      tmpl_values['HEAD'] += '  <link href="/css/main-%s.css?r=1" type="text/css" rel="stylesheet"/>\n' % style
    else:
      tmpl_values['HEAD'] += '  <link href="/css/main-%s.css?r=1" type="text/css" rel="stylesheet"/>\n' % config.DEFAULT_STYLE
    if style == 'light':
      tmpl_values['reCAPTCHA_THEME'] = '<script type="text/javascript">var RecaptchaOptions = {theme: "white"};</script>'
    else:
      tmpl_values['reCAPTCHA_THEME'] = '<script type="text/javascript">var RecaptchaOptions = {theme: "blackglass"};</script>'
  
  tmpl_values['config'] = config
  if request:
    tmpl_values['language_set_uri'] = request.language_set_uri

  path = os.path.join(os.path.dirname(__file__), '../tmpl/' + tmpl_name)
  
  render_html = template.render(path, tmpl_values)
  if response:
    response.out.write(render_html)
  return render_html
