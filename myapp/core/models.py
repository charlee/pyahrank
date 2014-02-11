# -*- coding: utf8 -*-

"""
Define common ops for data models
"""


#######################################################################
# DESIGN PRINCIPLE
#
# 1. Class must deal with all keys related to itself
# 2. Don't touch objects from other classes (these should go to core.*, not models)
# 3. Instance methods should not rely on fields other than id;
#    so that a reference returned by Class.ref() can call all instance methods
#
#######################################################################

import re
import datetime
from myapp import rds 
from myapp.utils.crypt import urlhash
from myapp.utils.common import random_string


# Link


class BaseModelMeta(type):

  def __init__(cls, name, bases, attrs):
    
    fields = {}

    # inherit fields from parent
    for base in bases:
      if hasattr(base, 'fields'):
        fields.update(base.fields)

    # overwrite base fields with own `fields`
    if attrs.has_key('fields'):
      fields = attrs['fields']

    # add extra fields if `extra_fields` defined
    if attrs.has_key('extra_fields'):
      fields.update(attrs['extra_fields'])

    cls.fields = fields

    # prepare for key name
    table_name = re.sub(r'([A-Z])', r'_\1', name)
    table_name = table_name[1:] if table_name[0] == '_' else table_name
    table_name = table_name.lower()

    cls.table_name = table_name

    # generate redis key name
    if not attrs.has_key('KEY'):
      cls.KEY = 'ah:' + table_name + ':%s'
      
    # generate auto_increment key name
    if not attrs.has_key('KEY_INCR'):
      cls.KEY_INCR = 'ah:' + table_name + ',incr'


class BaseHash:
  """Hash-type base model class"""

  __metaclass__ = BaseModelMeta

  def __init__(self, id, *args, **kwargs):

    # id is always str
    self.id = str(id)

    for field in self.fields.keys():

      default = self.fields[field]
      v = kwargs.get(field, str(default))

      # convert str to unicode
      if type(v) == str:
        v = v.decode('utf-8')

      setattr(self, field, v)


  @classmethod
  def seq(cls):
    """
    Get current sequence number
    """
    return rds.get(cls.KEY_INCR)

  def __repr__(self):
    keys = self.fields.keys()
    values = [getattr(self, key) for key in keys]
    values = [ x.encode('utf-8') if x is not None else None for x in values ]
    attrs = ', '.join('%s=%s' % pair for pair in zip(keys, values))

    return "<%s: id=%s, %s>" % (self.__class__.__name__, self.id, attrs)

  def __unicode__(self):
    return self.__repr__()

  def as_hash(self):
    h = { 'id': self.id }
    for field in self.fields.keys():
      h[field] = getattr(self, field)
    return h
      
  @classmethod
  def get(cls, id, fields=None):
    """
    Get a single object
    """
    if not id:
      return

    if not fields:
      fields = cls.fields.keys()

    if not cls.exists(id):
      return None

    result = rds.hmget(cls.KEY % id, fields)

    return cls(id, **dict(zip(fields, result)))

  @classmethod
  def mget(cls, ids, fields=None):
    """
    Get multiple objects (with pipeline)
    """
    if not ids:
      return []

    if not fields:
      fields = cls.fields.keys()

    p = rds.pipeline()
    for id in ids:
      p.hmget(cls.KEY % id, fields)

    result = p.execute()

    return map(lambda pair: cls(pair[0], **dict(zip(fields, pair[1]))),
               zip(ids, result))

  @classmethod
  def exists(cls, id):
    """
    Check if an id exists in the database
    """
    return rds.exists(cls.KEY % id)

  @classmethod
  def _filter_params(cls, params):
    """
    Filter kwargs to pre-defined fields
    """
    return dict((k, v) for (k, v) in params.iteritems() if k in cls.fields)

  @classmethod
  def ref(cls, id):
    """
    Get the object reference by id.
    This method makes sure that the id exists, but will not fill any fields.
    """
    if cls.exists(id):
      return cls(id)
    else:
      return None


  @classmethod
  def new(cls, id=None, **kwargs):
    """
    Add a new object and return added id
    """
    
    if not id:
      # generate auto increment id
      id = rds.incr(cls.KEY_INCR)
      while cls.exists(id):
        id = rds.incr(cls.KEY_INCR)

    # add data to db
    params = cls._filter_params(kwargs)
    rds.hmset(cls.KEY % id, params)

    return id
    

  def update(self, **kwargs):
    """
    Update current object
    """
    
    # update data to db
    params = self._filter_params(kwargs)
    rds.hmset(self.KEY % self.id, params)

    # update object
    for k, v in kwargs.iteritems():
      setattr(self, k, v)

  @classmethod
  def remove(cls, id):
    """
    Delete specified object
    """
    rds.delete(cls.KEY % id)

class BaseHashWithList(BaseHash):

  KEY_ALL = 'ah:' + table_name + ':all' 

  @classmethod
  def all(cls):
    return rds.lrange(cls.KEY_ALL, 0, -1)

  @classmethod
  def new(cls, id=None, **kwargs):
    realm_id = super(Realm, cls).new(id=id, **kwargs)
    rds.rpush(cls.KEY_ALL, realm_id)

    return realm_id

  @classmethod
  def remove(cls, id):
    rds.lrem(cls.KEY_ALL, id)
    super(Realm, cls).remove(id)


class Realm(BaseHashWithList):

  fields = {
    'name': '',
    'region': '',
  }

   
class Item(BaseHashWithList):

  fields = {
    'name': '',
    'item_class': 0,
    'item_sub_class': 0,
  }

class Auction(BaseHash):


