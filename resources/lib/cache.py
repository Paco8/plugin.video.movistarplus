# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import io
import os
import time
import glob
import sys

class Cache(object):
  config_directory = ''

  def __init__(self, config_directory):
    self.config_directory = config_directory

  def load_file(self, filename):
    filename = self.config_directory + filename
    if not os.path.exists(filename): return None
    with io.open(filename, 'r', encoding='utf-8') as handle:
      return handle.read()

  def save_file(self, filename, data):
    if sys.version_info[0] < 3:
      if not isinstance(data, unicode):
        data = unicode(data, 'utf-8')
    with io.open(self.config_directory + filename, 'w', encoding='utf-8', newline='') as handle:
      handle.write(data)

  def load(self, filename, cache_minutes = 24*60):
    filename = self.config_directory + filename
    if os.path.exists(filename) and (time.time() - os.path.getmtime(filename) < cache_minutes*60):
      with io.open(filename, 'r', encoding='utf-8') as handle:
        return handle.read()
    return None

  def remove_file(self, filename):
    filename = self.config_directory + filename
    if os.path.exists(filename):
      os.remove(filename)

  def clear_config(self):
    types = ('*.conf', '*.json')
    files = []
    for ext in types:
      files.extend(glob.glob(self.config_directory + ext))
    for filename in files:
      os.remove(filename)

  def clear_cache(self, days=10):
    from datetime import datetime
    deleted = 0
    files = glob.glob(os.path.join(self.config_directory + 'cache', '*.json'))
    now = datetime.now()
    for filename in files:
      modified_time = datetime.fromtimestamp(os.path.getmtime(filename))
      time_diff = now - modified_time
      if time_diff.days > days:
        os.remove(filename)
        deleted += 1
    return deleted
