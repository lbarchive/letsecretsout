from random import randint
import logging
import md5
import os
import re

from google.appengine.ext import db

from lso.util import get_gravatar, get_gravatar_check, is_email
import config


def get_length(length, lang):
  # length can be an int or a dict
  # If it is a dict, then the key is the language code with additional
  # 'default' key
  if isinstance(length, int):
    return length

  if lang not in length:
    lang = 'default'
  return length[lang]


class Secret(db.Model):

  subject = db.StringProperty(required=True)
  language = db.StringProperty(required=True)
  story = db.TextProperty(required=True)
  published = db.DateTimeProperty(required=True, auto_now_add=True)
  name = db.StringProperty()
  gravatar = db.ByteStringProperty()
  flags = db.IntegerProperty(default=0)
  hidden = db.BooleanProperty(default=False)
  tags = db.StringListProperty()

  def validate(self):

    for lang in config.VALID_LANGUAGES:
      if lang[0] == self.language:
        break
    else:
      raise ValueError(_('Incorrect language!'))
    
    if self.name:
      if len(self.name) < config.SECRET_NAME_MINLENGTH:
        raise ValueError(_('Name must be longer than %(length)d characters!') % {'length': config.SECRET_NAME_MINLENGTH})
      if len(self.name) > config.SECRET_NAME_MAXLENGTH:
        raise ValueError(_('Name must be shorter than %(length)d characters!') % {'length': config.SECRET_NAME_MAXLENGTH})
    
    minlength = get_length(config.SECRET_SUBJECT_MINLENGTH, self.language)
    if len(self.subject) < minlength:
      raise ValueError(_('Subject must be longer than %(length)d characters!') % {'length': minlength})
    if len(self.subject) > config.SECRET_SUBJECT_MAXLENGTH:
      raise ValueError(_('Subject must be shorter than %(length)d characters!') % {'length': config.SECRET_SUBJECT_MAXLENGTH})

    minlength = get_length(config.SECRET_STORY_MINLENGTH, self.language)
    if len(self.story) < minlength:
      raise ValueError(_('Story must be longer than %(length)d characters!') % {'length': minlength})
    if len(self.story) > config.SECRET_STORY_MAXLENGTH:
      raise ValueError(_('Story must be shorter than %(length)d characters!') % {'length': config.SECRET_STORY_MAXLENGTH})
  
    if self.tags:
      if len(self.tags) > config.SECRET_MAX_TAGS:
        raise ValueError(_('Only %(limit)d tags are allowed!') % {'limit': config.SECRET_MAX_TAGS})
      for tag in self.tags:
        if len(tag) > config.SECRET_TAG_MAXLENGTH:
          raise ValueError(_('Tag "%(tag)s" is too long, %(length)d characters is the limitation.') % {'tag': tag, 'length': config.SECRET_TAG_MAXLENGTH})

    if self._is_gravatar:
      if self._gravatar_check != get_gravatar_check(self.gravatar):
        raise ValueError(_('Gravatar Check is invalid!'))

  def set_gravatar(self, email='', gravatar_check=''):

    self._is_gravatar = False
    if is_email(email):
      self.gravatar = get_gravatar(email)
      self._is_gravatar = True
      self._gravatar_check = gravatar_check
    elif email:
      # That is not an emall address
      self.gravatar = md5.md5(email + config.SALT).digest()
    else:
      # Email is empty
      #name = self.name if self.name else 'anonymous'
      pass

  def set_tags(self, tags=''):

    tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
    # Remove duplicates
    new_tags = []
    for tag in tags:
      if tag not in new_tags:
        new_tags.append(tag)
    tags = new_tags

    if tags:
      self.tags = tags

  def get_gravatar_hash(self):

    if not hasattr(self, '_gravatar_hash'):
      self._gravatar_hash = ''.join(['%02x' % ord(x) for x in self.gravatar])
    return self._gravatar_hash

  def prepare_put(self, tags='', email='', gravatar_check=''):

    self.set_tags(tags)
    self.set_gravatar(email, gravatar_check)
    self.validate()

  def get_name(self):
    '''If name is not set, then return Anonymous or equal translation'''
    if self.name:
      if isinstance(self.name, unicode):
        return self.name.encode('utf-8')
      return self.name
    return _('Anonymous')

  def get_tags(self):

    return [tag.encode('utf-8') for tag in self.tags]

  def post_put(self):

    # Increase tag count
    if not self.tags:
      return
    key_names = ['%s_%s' % (self.language, tag) for tag in self.tags]
    tags = Tag.get_by_key_name(key_names)
    for i in range(len(key_names)):
      tag = tags[i]
      if tag:
        tag.count = tag.count + 1
      else:
        # new tag
        tag = Tag(key_name=key_names[i], name=self.tags[i], language=self.language, count = 1)
        tags[i] = tag
    db.put(tags)

  def incr_flags(self):

    self.flags = self.flags + 1
    if self.flags >= config.SECRET_FLAGS_TO_HIDE:
      self.hidden = True
    self.put()

  @classmethod
  def get_random(cls, language=''):
    
    q = cls.all()
    q.filter('hidden =', False)
    if language:
      q.filter('language =', language)
    q.order('-published')
    count = q.count()
    if count:
      if count > 100:
        count = 100
      secret = q.fetch(1, offset=randint(0, count - 1))[0]
    else:
      secret = None
    return secret        


class Tag(db.Model):

  name = db.StringProperty(required=True)
  language = db.StringProperty(required=True)
  count = db.IntegerProperty(default=0)
