# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app
from myapp.core.db import get_realms, get_all_item_ids, get_item, get_latest_price, get_item_classes, get_realm_by_name, get_all_prices
from myapp.utils.common import make_context, check_faction, parse_classinfo
from datetime import datetime, timedelta
from pytz import timezone

from .api import api

app.register_blueprint(api, url_prefix='/api')

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



@app.route('/p/<realm_name>/<faction_id><regex("(/[0-9,]*)?"):item_list>')
def price_list(realm_name, faction_id, item_list):

  realm = get_realm_by_name(realm_name)
  if realm is None:
    return _error(u"未找到服务器!")

  faction = check_faction(faction_id)

  if faction is None:
    return _error(u"阵营错误!")


  item_ids = map(int,item_list[1:].split(','))

  item_classes = get_item_classes()

  context = make_context({
    'realm': realm,
    'faction': faction,
    'item_ids': item_ids,
    'item_classes': format_item_classes(item_classes),
  })

  return render_template('trend.html', **context)


@app.route('/s/<realm_name>/<faction_id><regex("(/.*)?"):class_tag>')
def price_search(realm_name, faction_id, class_tag):

  realm = get_realm_by_name(realm_name)
  if realm is None:
    return _error(u"未找到服务器!")

  faction = check_faction(faction_id)

  if faction is None:
    return _error(u"阵营错误!")

  item_classes = get_item_classes()

  cls_tag = class_tag[1:]
  (cls_id, subcls_id) = parse_classinfo(cls_tag)
  
  cls_name = item_classes[cls_id]['name'] if cls_id else None
  subcls_name = item_classes[cls_id][subcls_id] if cls_id and subcls_id else None

  context = make_context({
    'realm': realm,
    'faction': faction,
    'cls_tag': class_tag[1:],
    'cls_id': cls_id,
    'cls_name': cls_name,
    'subcls_name': subcls_name,
    'item_classes': format_item_classes(item_classes),
  })

  return render_template('trend.html', **context)


def format_item_classes(item_classes):
  """ make item classes a better format for template output"""
  ret = []

  for clsid in sorted(item_classes.keys(), key=int):
    cls = {
      'id': clsid,
      'name': item_classes[str(clsid)]['name'],
      'subclasses': [],
    }

    for subclsid in sorted(filter(lambda x:x.isdigit(), item_classes[str(clsid)].keys()), key=int):
      cls['subclasses'].append({
        'id': subclsid,
        'name': item_classes[str(clsid)][str(subclsid)],
      })

    ret.append(cls)

  return ret



@app.route('/i/<realm_name>/<faction_id>/<int:item_id>')
def item_trend(realm_name, faction_id, item_id):

  realm = get_realm_by_name(realm_name)
  if realm is None:
    return _error(u"未找到服务器!")

  faction = check_faction(faction_id)

  if faction is None:
    return _error(u"阵营错误!")

  item = get_item(item_id)

  if not item:
    return _error(u"物品未找到!")

  prices = get_all_prices(realm['id'], faction['id'], item['id'])
  price_iter = iter(prices)
  
  trend_30days = []
  
  tz = timezone(app.config['TIMEZONE'])
  now = datetime.now(tz)
  today = datetime(now.year, now.month, now.day, tzinfo=tz)

  price = price_iter.next()
  price_date = datetime.fromtimestamp(price[0] / 1000, tz)

  try:
    for i in xrange(30):
      
      current_date = today - timedelta(days=i)        # current day
      next_date = current_date + timedelta(days=1)    # the day after current day

      # skip those newer than next_day
      while price_date > next_date:
        price = price_iter.next()
        price_date = datetime.fromtimestamp(price[0] / 1000, tz)
      
      # now here's the data closest to the current day
      if price_date >= current_date:
        trend_30days.append({
          'lastUpdate': current_date.strftime('%m/%d'),
          'quantity': price[1],
          'average': price[2],
          'min_price': price[3],
        })

      # oh..the closest data does not exist
      else:
        trend_30days.append({
          'lastUpdate': current_date.strftime('%m/%d'),
          'quantity': 0,
          'average': 0,
          'min_price': 0,
        })
  except StopIteration:
    pass

  # put latest data on the right most side
  trend_30days.reverse()
  
  context = make_context({
    'realm': realm,
    'faction': faction,
    'item': item,
    'trend_30days': trend_30days,
  })

  return render_template('item.html', **context)
