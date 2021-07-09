#!/bin/env python3

from os import listdir
from os import getcwd

short_date = getcwd().split('/').pop(-1).split(' ').pop(0)
year = '20' + short_date[0:2]
month = short_date[2:4]

output = []
for file in listdir():
  if file.split('.').pop(-1) != 'xlsx':
    output.append('<a href="/wp-content/uploads/20'+short_date[0:2]+'/'+short_date[2:4]+'/'+file+'">'+file.split('.').pop(-1)+'</a>')
  else:
    output.append('<a href="/wp-content/uploads/20'+short_date[0:2]+'/'+short_date[2:4]+'/'+file+'">excel</a>')

print('(' + ', '.join(output)+')')

