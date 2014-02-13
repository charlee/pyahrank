#!/usr/bin/env python

import sys

from myapp import app

def run_cron(cmd):

  crontask = None
  try:
    crontask = __import__("myapp.cron.%s" % cmd, globals(), locals(), ['run'], -1)
  except ImportError:
    print "Command `%s' not found" % cmd

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
