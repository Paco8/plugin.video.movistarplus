#!/usr/bin/env python
# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

from datetime import datetime
import pytz
from dateutil import parser

weekdays = ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']

def timestamp2str(timestamp, format='%H:%M'):
  time = datetime.fromtimestamp(timestamp / 1000)
  if '%a' in format:
    w = int(time.strftime('%w'))
    format = format.replace('%a', weekdays[w])
  return time.strftime(format).capitalize()

def isodate2date(date_string):
  date_object = parser.parse(date_string)
  if date_object.tzinfo is None:
    madrid_tz = pytz.timezone("Europe/Madrid")
    madrid_time = madrid_tz.localize(date_object)
  else:
    madrid_time = date_object.astimezone(pytz.timezone("Europe/Madrid"))
  return madrid_time

def isodate2str(date_string):
  try:
    date_object = isodate2date(date_string)
    return date_object.strftime("%d/%m/%Y %H:%M:%S")
  except:
    return date_string
