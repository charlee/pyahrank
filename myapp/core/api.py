# -*- coding: utf8 -*-

import json
import requests
import gzip
from myapp.core.cache import get_cached_content, set_cached_content
from StringIO import StringIO

class WowApi:

  def __init__(self, realm):
    self.realm = realm
    self.server = 'www.battlenet.com.cn'
    
    
  def _get_url(self, part):
    return 'http://%s/api/wow/%s' % (self.server, part)


  def get_content(self, url, cache=False):

    if cache:
      data = get_cached_content(url)
      if data is not None:
        return data

    r = requests.get(url)
    data = r.content

    # cache content if needed
    if cache:
      set_cached_content(url, data)
    
    return data
    

  def auction(self):
    url = self._get_url('auction/data/' + self.realm['name'].encode('utf-8'))
    res = self.get_content(url)
    
    return json.loads(res)


  def item(self, id):
    url = self._get_url('item/' + id)
    res = self.get_content(url)
    return json.loads(res)


    
