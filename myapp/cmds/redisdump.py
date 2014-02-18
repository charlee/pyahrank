# -*- coding: utf8 -*-

import sys
import json

from myapp import rds

from myapp.core.db import _key



class RedisExport(object):

  def __init__(self, path):
    self.fh = open(path, 'w')

  def close(self):
    self.fh.close()

  def dump_string(self, key):
    value = rds.get(key)
    self.fh.write('%s|%s|%s\n' % (key, 'string', value))
    return value
    
  def dump_list(self, key):
    value = rds.lrange(key, 0, -1)
    self.fh.write('%s|%s|%s\n' % (key, 'list', json.dumps(value)))
    return value

  def dump_hash(self, key):
    value = rds.hgetall(key)
    self.fh.write('%s|%s|%s\n' % (key, 'hash', json.dumps(value)))
    return value

  def dump_set(self, key):
    value = rds.smembers(key)
    self.fh.write('%s|%s|%s\n' % (key, 'set', json.dumps(list(value))))


class RedisImport(object):

  def __init__(self, path):
    self.path = path

  def loads(self, s):

    (key, key_type, value) = s.split('|', 2)
    if key_type == 'string':
      rds.set(key, value)
    elif key_type == 'list':
      rds.rpush(key, *(json.loads(value)))
    elif key_type == 'hash':
      rds.hmset(key, json.loads(value))
    elif key_type == 'set':
      rds.sadd(key, *(json.loads(values)))

  def import_all(self):
    fh = open(self.path)
    lines = fh.readlines()
    for line in lines:
      self.loads(line)

    fh.close()


def export_redis(path):

  rd = RedisExport(path)
  
  rd.dump_string(_key('realms'))
  rd.dump_string(_key('items:classes'))

  items_queue = rd.dump_set(_key('items:queue'))
  items_list = rd.dump_set(_key('items:list'))

  for item_id in items_list:
    rd.dump_hash(_key('item:%s', item_id))

  rd.close()

def import_redis(path):
  rd = RedisImport(path)
  rd.import_all()


def run():
  if len(sys.argv) < 4:
    help()

  else:
    action = sys.argv[2]
    filename = sys.argv[3]
    if action == 'import':
      import_redis(filename)
    elif action == 'export':
      export_redis(filename)
    else:
      help()


def help():
  print "Usage: %s export|import <filename>" % sys.argv[0]
