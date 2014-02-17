#!/usr/bin/env python

import os
import sys

BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASEDIR)

from myapp import app

def run_cron(cmd):

  crontask = None
  try:
    crontask = __import__("myapp.cron.%s" % cmd, globals(), locals(), ['run'], -1)
  except ImportError as e:
    print "Cannot load Command `%s': %s" % (cmd, e)

  if crontask is not None:
    crontask.run()


def show_help():
  pass


if __name__ == '__main__':

  if len(sys.argv) < 2:
    show_help()
    
  else:
    cmd = sys.argv[1]
    run_cron(cmd)
