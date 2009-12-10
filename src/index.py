from random import randint
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from lso.models import Secret
from lso.util import I18NRequestHandler
from lso.ui import render_write
import config


class HomePage(I18NRequestHandler):
  # XXX
  DEFS = [
      '<a href="http://dictionary.cambridge.org/define.asp?key=71037&amp;dict=CALD"><tt>secret</tt></a><br/><i>noun</i> a piece of information that is only known by one person or a few people and should not be told to others. (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://dictionary.cambridge.org/define.asp?key=71041&amp;dict=CALD"><tt>secret</tt></a><br/><i>adj.</i> If something is secret, other people are not allowed to know about it. (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://dictionary.cambridge.org/define.asp?key=16073&amp;dict=CALD"><tt>confess</tt></a><br/><i>verb</i> to admit that you have done something wrong or something that you feel guilty or bad about. (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://dictionary.cambridge.org/define.asp?key=16076&amp;dict=CALD"><tt>confession</tt></a><br/><i>verb</i> when you admit that you have done something wrong or illegal . (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://dictionary.cambridge.org/define.asp?key=100230&amp;dict=CALD"><tt>embarrassed</tt></a><br/><i>adj.</i> feeling ashamed or shy. (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://dictionary.cambridge.org/define.asp?key=4266&amp;dict=CALD"><tt>ashamed</tt></a><br/><i>adj.</i> feeling guilty or embarrassed about something you have done or a quality in your character. (Cambridge Advanced Learner\'s Dictionary. 2009)',
      '<a href="http://www.askoxford.com/concise_oed/confess?view=uk"><tt>confess</tt></a><br/><i>verb</i> admit to a crime or wrongdoing. (Compact Oxford English Dictionary. 2009)',
      '<a href="http://www.askoxford.com/concise_oed/confession?view=uk"><tt>confession</tt></a><br/><i>noun</i> an act of confessing, especially a formal statement admitting to a crime. (Compact Oxford English Dictionary. 2009)',
      '<a href="http://www.askoxford.com/concise_oed/guilty?view=uk"><tt>guilty</tt></a><br/><i>adj.</i> (often guilty of) responsible for a specified wrongdoing, fault, or error. (Compact Oxford English Dictionary. 2009)',
      '<a href="http://www.askoxford.com/concise_oed/depressed?view=uk"><tt>depressed</tt></a><br/><i>adj.</i> severely despondent and dejected. (Compact Oxford English Dictionary. 2009)',
      '<a href="http://www.askoxford.com/concise_oed/ashamed?view=uk"><tt>ashamed</tt></a><br/><i>adj.</i> feeling embarrassed or guilty. (Compact Oxford English Dictionary. 2009)',
      '<a href="http://www.merriam-webster.com/dictionary/secret%5B2%5D"><tt>secret[2]</tt></a><br/><i>noun</i> something kept from the knowledge of others or shared only confidentially with a few. (Merriam-Webster Online Dictionary. 2009)',
      ]

  def get(self):
    
    secret = Secret.get_random(self.request.LANGUAGE_CODE)
    tmpl_values = {
        # XXX
        'DEFS': self.DEFS,
        'secret': secret,
        }

    render_write(tmpl_values, 'home.html', self.request, self.response)

  def head(self):

    pass


class StaticPage(I18NRequestHandler):

  def get(self, pagename):
 
    render_write({}, pagename + '.html', self.request, self.response)

  def head(self):

    pass


application = webapp.WSGIApplication([
    ('/', HomePage),
    ('/(about|terms|faq)', StaticPage),
    ],
    debug=config.DEBUG)


def main():
  
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
