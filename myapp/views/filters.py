
from myapp import app
import json

def pretty_price(value):
  value = int(value)
  g = value / 10000
  s = (value % 10000) / 100
  c = value % 100

  value = ''
  if g: value += str(g) + '.'
  if s: value += str(s) + '.'
  value += str(c)

  return value


def tojson(value):
  return json.dumps(value)

# add template filters
app.jinja_env.filters['pretty_price'] = pretty_price
app.jinja_env.filters['json'] = tojson
