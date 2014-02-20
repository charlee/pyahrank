# -*- coding: utf8 -*-

from myapp.core.db import get_item, get_all_item_ids, classify_item

def reclassify_items():

  item_ids = get_all_item_ids()

  print "Total %s items to classify..." % len(item_ids)

  counter = 0

  for item_id in item_ids:
    item = get_item(item_id)
    classify_item(item)
    counter += 1

  print "%s items classified." % counter


def run():
  reclassify_items()
