# -*- coding: utf8 -*-

import sys
import json
import time
import requests
import gzip
from myapp.core.cache import get_cached_content, set_cached_content
from StringIO import StringIO

MAX_RETRY = 3

class WowApi:

  def __init__(self, realm=None):
    self.realm = realm
    self.server = 'www.battlenet.com.cn'
    
    
  def _get_url(self, part):
    return 'http://%s/api/wow/%s' % (self.server, part)


  def get_content(self, url):

    retry = 0
    while retry < MAX_RETRY:
      try:
        r = requests.get(url)
        data = r.content

        break

      except requests.exceptions.ConnectionError as e:
        retry += 1
        time.sleep(retry * 5)
        print "Failed, retry in %s seconds..." % (retry * 5)
        if retry >= MAX_RETRY:
          raise e
        
    return data


  def get_auctions_file(self, url, lastModified, cache=True):
    
    data = get_cached_content(url, lastModified)
    if data is not None:
      return data

    response = requests.get(url, stream=True)

    dl = 0
    data = ''
    for chunk in response.iter_content():
      dl += len(chunk)
      data += chunk
      sys.stdout.write("\r%sKB downloaded" % (dl / 1024) )
      sys.stdout.flush()

    # cache content if needed
    if cache:
      set_cached_content(url, data, lastModified)

    return data
    
  def auction(self):
    url = self._get_url('auction/data/' + self.realm['name'].encode('utf-8'))
    res = self.get_content(url)
    
    return json.loads(res)


  def item(self, id):
    url = self._get_url('item/' + id)
    res = self.get_content(url)
    return json.loads(res)


  def item_classes(self):
    url = self._get_url('data/item/classes')
    res = self.get_content(url)
    return json.loads(res)
    
    
