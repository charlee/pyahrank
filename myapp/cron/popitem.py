# -*- coding: utf8 -*-

import json
from myapp.core.api import WowApi
from myapp.core.db import get_all_item_ids, get_queued_item_ids, populate_item



def populate_all_items():

  api = WowApi(None)

  queued_item_ids = get_queued_item_ids()
  for item_id in queued_item_ids:

    print "populating item %s..." % item_id,

    res = api.item(item_id)

    item = {}
    for key in ('id', 'name', 'itemClass', 'itemSubClass', 'buyPrice', 'sellPrice', 'inventoryType', 'quality'):
      item[key] = res[key]

    print item['name']

    populate_item(item)


def run():
  populate_all_items()
  
