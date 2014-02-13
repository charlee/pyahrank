# -*- coding:utf8 -*-

from flask import render_template, session
from myapp import app

@app.route('/')
def index():

  return render_template('index.html', **context)

