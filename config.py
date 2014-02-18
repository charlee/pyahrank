# -*- coding: utf8 -*-

import os

class Config(object):
  DEBUG = True
  BASEDIR = os.path.abspath(os.path.dirname(__file__))

  HOST = '0.0.0.0'
  PORT = 8000

  TIMEZONE = 'Asia/Shanghai'

  # redis db config
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  REDIS_DB = 0
  REDIS_PASSWORD = None

class Development(Config):
  pass

class Production(Config):
  DEBUG = False
  HOST = '127.0.0.1'
  PORT = 2401
  REDIS_DB = 2
