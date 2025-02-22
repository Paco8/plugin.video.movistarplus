# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import requests
import ssl
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

class CustomAdapter(HTTPAdapter, object):
  if sys.version_info[0] == 3:
    def init_poolmanager(self, connections, maxsize, block=False):
      ctx = ssl.create_default_context()
      self.poolmanager = PoolManager(
          num_pools=connections,
          maxsize=maxsize,
          block=block,
          ssl_context=ctx
      )

class MySession(requests.Session, object):
  def __init__(self, *args, **kwargs):
    super(MySession, self).__init__(*args, **kwargs)
    if sys.platform.startswith("linux") and sys.version_info[0] == 3:
      self.mount('https://', CustomAdapter())
