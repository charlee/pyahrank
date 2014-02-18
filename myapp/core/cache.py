# -*- coding: utf8 -*-

import re
import os
from myapp import app

CACHEDIR = os.path.join(app.config['BASEDIR'], 'cache')

def _get_cache_path(url, extra):
  
  fn = "%s-%s" % (extra, re.sub(r'[\\/:&?]', '_', url))
  path = os.path.join(CACHEDIR, fn)

  return path

def get_cached_content(url, extra):

  path = _get_cache_path(url, extra)

  try:
    return open(path).read()
  except IOError:
    return None

def set_cached_content(url, content, extra):

  path = _get_cache_path(url, extra)
  open(path, 'w').write(content)
  
