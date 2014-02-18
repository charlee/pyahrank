# -*- coding: utf8 -*-

import json
from myapp.core.api import WowApi
from myapp.core.db import get_realms, set_realms, get_all_item_ids, get_queued_item_ids, request_item, add_price, get_latest_price


def get_all_auctions():

  realms = get_realms()
  for realm in realms:
    if realm['active']:

      api = WowApi(realm)
      (url, lastModified) = request_auctions_file_url(api)
      get_auctions(api, url, lastModified)


def request_auctions_file_url(api):

  res = api.auction()
  if 'files' in res:
    f = res['files'][0]
    return ( f['url'], f['lastModified'] )


def get_auctions(api, url, lastModified):
  
  print 'loading auctions file from %s...' % api.realm['name'].encode('utf-8')
  res = api.get_auctions_file(url, lastModified, cache=True)
  data = json.loads(res)

  print "data download completed"

  print "processing alliance data"
  process_ah(data['alliance']['auctions'], 'alliance', api.realm['id'], lastModified)

  print "processing horde data"
  process_ah(data['horde']['auctions'], 'horde', api.realm['id'], lastModified)
  

def process_ah(auctions, faction, realm_id, lastModified):

  items = {}

  for auction in auctions:

    if auction['item'] not in items:
      items[auction['item']] = {}

    item = items[auction['item']]

    # init item buyout
    if 'price' not in item:
      item['price'] = {}

    # ignore bid only items
    if int(auction['buyout']) > 0:
      
      # init price counter
      price = int(round(auction['buyout'] / auction['quantity']))
      if price not in item['price']:
        item['price'][price] = 0;
      item['price'][price] += auction['quantity'];


    # write back
    items[auction['item']] = item;

  existing_item_ids = get_all_item_ids().union(get_queued_item_ids())

  price_counter = 0
  queue_counter = 0
  
  for item_id, item in items.iteritems():
    if item['price']:
      
      (timestamp, price, quantity) = get_latest_price(realm_id, faction, item_id)
      if int(timestamp) != int(lastModified):

        (average, quantity) = calculate_average_without_outliers(item['price'])

        # write to db
        add_price(realm_id, faction, item_id, lastModified, average, quantity)
        price_counter += 1

        if str(item_id) not in existing_item_ids:
          print "request item %s" % item_id
          request_item(item_id)
          queue_counter +=1 

  print "%s price(s) recorded, %s item(s) requested" % (price_counter, queue_counter)


def calculate_average_without_outliers(prices):
  

  total_qty = sum(prices.values())
  price_list = prices.keys()

  price_list.sort()

  start = round(total_qty / 10) if total_qty >= 10 else 1
  end = round(total_qty * 5 / 10) if total_qty >= 10 else total_qty


  qty = 0           # acdtually qty is a counter indicates where we are in the prices
  total_price = 0

  for price in price_list:
    this_qty = max(0, min(qty + prices[price], end) - max(qty, start) + 1)
    total_price += this_qty * price;
    qty += prices[price]

  average = int(round(total_price) / (end - start + 1))

  return (average, total_qty)



def run():
#  realms = get_realms() 
#  realms.append({
#    'id': 1,
#    'name': '太阳之井',
#    'region': 'cn',
#    'active': True
#  });
#  set_realms(realms)
  get_all_auctions()
