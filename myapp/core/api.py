# -*- coding: utf8 -*-

import json
import urllib2
import gzip
from StringIO import StringIO

class WowApi:

  def __init__(self, realm):
    self.realm = realm
    self.server = 'www.battlenet.com.cn'
    
    
  def _get_url(self, part):
    return 'http://%s/api/wow/%s' % (self.server, part)


  def get_content(self, url):

    req = urllib2.Request(url)
    req.add_header('Accept-encoding', 'gzip')
    res = urllib2.urlopen(req)

    if res.info().get('Content-Encoding') == 'gzip':
      buf = StringIO(res.read())
      f = gzip.GzipFile(fileobj=buf)
      data = f.read()

    else:
      data = res.read()
    
    return data
    

  def auction(self):
    url = self._get_url('auction/data/' + self.realm['name'].encode('utf-8'))
    res = self.get_content(url)
    
    return json.loads(res)


  def item(self, id):
    url = self._get_url('item/' + id)
    res = self.get_content(url)
    return json.loads(res)


    
