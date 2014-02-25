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

def get_realm_by_name(realm_name):
  realms = filter(lambda x:x['name'] == realm_name, get_realms())
  return realms[0] if realms else None

  
def set_realms(realms):
  rds.set(_key('realms'), json.dumps(realms))


def get_item(item_id):
  res = rds.hgetall(_key('item:%s', item_id))
  for k in res.keys():
    res[k] = res[k].decode('utf-8')

  return res

def get_items(item_ids):
  p = rds.pipeline()
  for item_id in item_ids:
    p.hgetall(_key('item:%s', item_id))
  
  items = list(p.execute())
  for item in items:
    if item:
      for k in item.keys():
        item[k] = item[k].decode('utf-8')

  return items

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


def add_price(realm_id, faction, item_id, timestamp, qty, avg, min_price):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  data = '%s:%s:%s:%s' % (timestamp, qty, avg, min_price)
  rds.lpush(key, data)


def get_all_prices(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  return rds.lrange(key, 0, -1)

def get_latest_price(realm_id, faction, item_id):
  key = _key('price:%s:%s:%s', realm_id, faction, item_id)
  result = rds.lrange(key, 0, 0)
  if result:
    (timestamp, qty, avg, min_price) = result[0].split(':')
    return int(timestamp), int(qty), int(avg), int(min_price)
  else:
    return (0, 0, 0, 0)

def get_latest_price_multi(realm_id, faction, item_ids):
  keys = map(lambda x:_key('price:%s:%s:%s', realm_id, faction, x), item_ids)
  p = rds.pipeline()
  for key in keys:
    p.lrange(key, 0, 0)

  results = []
  for result in p.execute():
    if result:
      (timestamp, qty, avg, min_price) = result[0].split(':')
      results.append((int(timestamp), int(qty), int(avg), int(min_price)))
    else:
      results.append((0, 0, 0, 0))

  return results
  
def set_item_classes(item_classes):
  """
  Set the item classes
  """
  key = _key('items:classes')
  s = json.dumps(item_classes)
  rds.set(key, s)

def get_item_classes():
  """
  Returns the item classes
  """
  key = _key('items:classes')
  s = rds.get(key)
  try:
    o = json.loads(s)
  except (TypeError, ValueError):
    o = {}

  return o


def classify_item(item):
  """
  Put specified item to corresponding item list
  """

  if str(item['itemClass']).isdigit() and str(item['itemSubClass']).isdigit():
    key = _key('items:class:%s.%s', item['itemClass'], item['itemSubClass'])
    rds.sadd(key, '%s:%s:%s' % (item['id'], item['name'], item['quality']))
    


def search_items(cls_id=None, subcls_id=None, item_range=None, keyword=None, quality=None, sort='+name'):
  """
  Get item ids by class id and subclass id
  range: tuple (start, count)
  """

  item_classes = get_item_classes()

  # generate item list
  cls = item_classes.get(str(cls_id)) if cls_id is not None else None
  if cls:
    if subcls_id is None:
      subcls_ids = filter(lambda x:x != 'name', cls.keys())
      keys = map(lambda x:_key('items:class:%s.%s', cls_id, x), subcls_ids)
    
    else:
      keys = [ _key('items:class:%s.%s' % (cls_id, subcls_id)) ]

  else:
    keys = []

    for cls_id, cls in item_classes.iteritems():
      subcls_ids = filter(lambda x:x != 'name', cls.keys())
      keys += map(lambda x:_key('items:class:%s.%s', cls_id, x), subcls_ids)

    
  item_idx = rds.sunion(keys)
  item_idx = filter(lambda x:len(x)==3, map(lambda x:x.split(':'), item_idx))

  if keyword is not None:
    keyword = keyword.encode('utf-8')
    item_idx = filter(lambda x:keyword in x[1], item_idx)

  if quality is not None:
    item_idx = filter(lambda x:str(quality) == x[2], item_idx)

  reverse_sort = (sort[0] == '-')
  if sort[1:] == 'name':
    item_idx.sort(key=lambda x:x[1], reverse=reverse_sort)
  elif sort[1:] == 'quality':
    item_idx.sort(key=lambda x:x[2], reverse=reverse_sort)

  total = len(item_idx)

  if item_range is not None:
    item_idx = item_idx[item_range[0]:(item_range[0]+item_range[1])]

  # get items
  item_ids = map(lambda x:x[0], item_idx)

  return (total, item_ids)
