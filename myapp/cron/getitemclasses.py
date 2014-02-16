# -*- coding: utf8 -*-

import json
from myapp.core.api import WowApi
from myapp.core.db import set_item_classes


def run():

  api = WowApi()
  orig = api.item_classes()

  item_classes = {}

  for o in orig['classes']:
    class_id = o['class']
    item_classes[class_id] = dict((sc['subclass'], sc['name']) for sc in o['subclasses'])
    item_classes[class_id]['name'] = o['name']

  set_item_classes(item_classes)

