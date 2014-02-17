#!/usr/bin/env python
# -*- coding:utf8 -*-

from myapp import app

if __name__ == '__main__':

  app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])


