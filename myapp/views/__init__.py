# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app
from myapp.core.db import get_realms, get_all_item_ids, get_item
from myapp.utils.common import make_context

@app.route('/')
def index():

  realms = get_realms()

  context = make_context({ 'realms': realms })

  return render_template('index.html', **context)



@app.route('/<realm_name>/<faction_name>')
def trend(realm_name, faction_name):

  realms = get_realms()

  realms = filter(lambda x:x['name'] == realm_name, realms)

  if len(realms) < 1:

    context = make_context({
      'error': u"未找到服务器!"
    });

  else:
    realm = realms[0]
    faction = u'联盟' if faction_name == 'alliance' else u'部落'
    
    context = make_context({
      'realm': realm['name'],
      'faction': faction
    })

  return render_template('trend.html', **context)
