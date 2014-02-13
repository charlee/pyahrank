# -*- coding: utf8 -*-

import json
from myapp import rds 

KEY_PREFIX = 'ahr'

def _key(key, *args):
  return KEY_PREFIX + ":" + key % args


def get_realms():

  realms = rds.get(_key('realms'))
  if not realms:
    realms = '[]'
  return json.loads(realms)
  
def set_realms(realms):
  rds.set(_key('realms'), json.dumps(realms))


def get_item(item_id):
  fields = [
    'id',
    'name',
    'item_class',
    'item_subclass'
  ]
  return rds.hmget(_key('item:%s', item_id), fields)

def get_all_item_ids():
  return rds.lrange(_key('items:list'), 0, -1);

def get_queued_item_ids():
  return rds.lrange(_key('items:queue'), 0, -1);

def populate_item(item):
  item_id = item['id']
  rds.hmset(_key('item:%s', item_id), item)     # populate item content
  rds.lrem(_key('items:queue'), item_id)        # remove it from queue
  rds.rpush(_key('items:list'), item_id)        # and add it to items list

def request_item(item_id):
  rds.rpush(_key('items:list'), item_id)        # push it to queue



def add_price(realm_id, faction, item_id, timestamp, avg, qty):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  data = '%s:%s:%s' % (timestamp, avg, qty)
  rds.lpush(key, data)


def get_all_prices(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  return rds.lrange(key, 0, -1)

def get_latest_price(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  return rds.lrange(key, 0, 0)
  
