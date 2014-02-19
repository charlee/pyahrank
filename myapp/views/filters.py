
from myapp import app

def pretty_price(value):
  value = int(value)
  g = value / 10000
  s = (value % 10000) / 100
  c = value % 100

  value = ''
  if g: value += str(g) + 'g'
  if s: value += str(s) + 's'
  value += str(c) + 'c'

  return value


# add template filters
app.jinja_env.filters['pretty_price'] = pretty_price

