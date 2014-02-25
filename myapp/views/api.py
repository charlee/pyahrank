# -*- coding:utf8 -*-


from myapp import app
from myapp.core.db import get_items, search_items, get_realm_by_name, get_latest_price_multi
from myapp.utils.common import parse_classinfo, check_faction
from flask import Blueprint, request, jsonify, abort, make_response
from flask.ext.csrf import csrf_exempt
from datetime import datetime
from pytz import timezone

PAGESIZE = 50

api = Blueprint('api', __name__)

def _error(msg):
  return jsonify({ 'error': msg })

@api.route('/<realm_name>/<faction_id>/prices_search')
def prices_search(realm_name, faction_id):

  realm = get_realm_by_name(realm_name)
  if realm is None:
    return _error(u"未找到服务器！")

  faction = check_faction(faction_id)
  if faction is None:
    return _error(u"阵营错误!")

  cls_tag = request.args.get('cls', '')
  cls_id, subcls_id = parse_classinfo(cls_tag)
  page = request.args.get('p', '1')
  keyword = request.args.get('k', None)
  sort = request.args.get('s', None)
  quality = request.args.get('q', None)

  if cls_id is None and keyword is None and quality is None:
    total = 0
    results = []
    rng = (0, 0)
  else:
    (total, item_ids) = search_items(cls_id, subcls_id, ((int(page) - 1) * PAGESIZE, PAGESIZE), keyword, sort)
    results = get_prices(realm['id'], faction['id'], item_ids)
    start = (int(page) - 1) * PAGESIZE + 1
    end = start + PAGESIZE - 1
    if end > total:
      end = total
    rng = (start, end)

  return jsonify(items=results, total=total, range=rng)



@api.route('/<realm_name>/<faction_id>/item_list/<regex("[0-9,]*"):item_list>')
def prices_by_items(realm_name, faction_id, item_list):

  realm = get_realm_by_name(realm_name)
  if realm is None:
    return _error(u"未找到服务器!")

  faction = check_faction(faction_id)

  if faction is None:
    return _error(u"阵营错误!")

  item_ids = item_list.split(',')

  results = get_prices(realm['id'], faction['id'], item_ids)


  return jsonify(items=results)
  

def get_prices(realm_id, faction, item_ids):

  prices = get_latest_price_multi(realm_id, faction, item_ids)

  items = get_items(item_ids)

  results = []

  tz = timezone(app.config['TIMEZONE'])

  for i in xrange(len(item_ids)):
    if items[i] and prices[i][0]:
      items[i].update({
        'lastUpdate': datetime.fromtimestamp(prices[i][0] / 1000, tz).strftime('%Y/%m/%d %H:%H'),
        'quantity': prices[i][1],
        'average': prices[i][2],
        'min_price': prices[i][3],
      })

      results.append(items[i])

  return results
