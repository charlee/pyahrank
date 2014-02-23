# -*- coding:utf8 -*-

import random
import re

def make_context(params):
    
  context = {}

  context.update(params)

  return context

def check_faction(faction_name):
  if faction_name == 'alliance':
    return { 'id': 'alliance', 'name': u'联盟' };
  elif faction_name == 'horde':
    return { 'id': 'horde', 'name': u'部落' };
  else:
    return None


def parse_classinfo(class_tag):
  """parses the class info in the url"""

  m = re.match(r'^(\d+)(\.(\d+))?$', class_tag)
  if m:
    cls = m.group(1)
    subcls = m.group(3) or None

    return cls, subcls

  else:
    return (None, None)

    
