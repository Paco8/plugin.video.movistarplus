#!/usr/bin/env python
# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

from datetime import datetime, timedelta

def timestamp2str(timestamp):
  time = datetime.fromtimestamp(timestamp / 1000)
  return time.strftime("%H:%M")

def isodate2str(iso_str):
  iso_str = iso_str[0:19]
  try:
    dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
  except:
    return iso_str

  try:
    import pytz
    utc_tz = pytz.timezone('UTC')
    dt = utc_tz.localize(dt)
    dt = dt.astimezone(pytz.timezone('Europe/Madrid'))
  except:
    pass

  dt = dt.strftime('%d/%m/%Y %H:%M:%S')
  return dt

