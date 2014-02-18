# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app
from myapp.core.db import get_realms, get_all_item_ids, get_item, get_latest_price, get_item_classes
from myapp.utils.common import make_context
from datetime import datetime
from pytz import timezone


def _error(msg):

  context = make_context({
    'error': msg,
  })

  return render_template('error.html', **context)
  

@app.route('/')
def index():

  realms = get_realms()

  context = make_context({ 'realms': realms })

  return render_template('index.html', **context)



@app.route('/<realm_name>/<faction_name><regex("(/[0-9,]*)?"):item_list>')
def trend(realm_name, faction_name, item_list):

  realms = get_realms()

  realms = filter(lambda x:x['name'] == realm_name, realms)

  if len(realms) < 1:
    return _error(u"未找到服务器!")

  if faction_name not in ('alliance', 'horde'):
    return _error(u"阵营错误!")


  # start to get prices
  realm = realms[0]
  faction = u'联盟' if faction_name == 'alliance' else u'部落'

  item_ids = item_list[1:].split(',')

  items = []

  item_classes = get_item_classes()

  tz = timezone(app.config['TIMEZONE'])

  for item_id in item_ids:
    (timestamp, price, quantity) = get_latest_price(realm['id'], faction_name, item_id)
    if timestamp:
      item = get_item(item_id)

      item_class = item_classes.get(item['itemClass'], {}).get('name', '-')
      item_subclass = item_classes.get(item['itemClass'], {}).get(item['itemSubClass'], '-')

      items.append({
        'id': item_id,
        'name': item and item['name'] or '(未知)',
        'price_g': price / 10000,
        'price_s': (price % 10000) / 100,
        'price_c': price % 100,
        'quality': item and item['quality'] or '1',
        'quantity': quantity,
        'lastUpdate': datetime.fromtimestamp(timestamp / 1000, tz).strftime('%Y/%m/%d %H:%M'),
        'itemClass': item_class,
        'itemSubClass': item_subclass,
      })

  
  context = make_context({
    'realm': realm['name'],
    'faction_name': faction_name,
    'faction': faction,
    'items': items
  })

  return render_template('trend.html', **context)
