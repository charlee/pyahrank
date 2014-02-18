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
    'itemClass',
    'itemSubClass',
    'quality',
    'inventoryType',
    'buyPrice',
    'sellPrice',
  ]
  res = rds.hmget(_key('item:%s', item_id), fields)

  return dict(zip(fields, map(lambda x:x.decode('utf-8'), res)))

def get_all_item_ids():
  return rds.smembers(_key('items:list'))

def get_queued_item_ids():
  return rds.smembers(_key('items:queue'))

def populate_item(item):
  item_id = item['id']
  rds.hmset(_key('item:%s', item_id), item)     # populate item content
  rds.smove(_key('items:queue'), _key('items:list'), item_id)   # remove it from queue and add it to items list

def request_item(item_id):
  rds.sadd(_key('items:queue'), item_id)        # push it to queue


def add_price(realm_id, faction, item_id, timestamp, avg, qty):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  data = '%s:%s:%s' % (timestamp, avg, qty)
  rds.lpush(key, data)


def get_all_prices(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  return rds.lrange(key, 0, -1)

def get_latest_price(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  result = rds.lrange(key, 0, 0)
  if result:
    (timestamp, price, quantity) = result[0].split(':')
    return int(timestamp), int(price), int(quantity)
  else:
    return (0, 0, 0)
  
def set_item_classes(item_classes):
  key = _key('items:classes')
  s = json.dumps(item_classes)
  rds.set(key, s)

def get_item_classes():
  key = _key('items:classes')
  s = rds.get(key)
  return json.loads(s)
