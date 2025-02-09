# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import requests

import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

class CustomAdapter(HTTPAdapter, object):
  try:
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    def init_poolmanager(self, connections, maxsize, block=False):
      self.poolmanager = PoolManager(
          num_pools=connections,
          maxsize=maxsize,
          block=block,
          ssl_version=ssl.PROTOCOL_TLS,
          ssl_context=self.ctx
      )
  except:
    pass

class MySession(requests.Session, object):
  def __init__(self, *args, **kwargs):
    super(MySession, self).__init__(*args, **kwargs)
    self.mount('https://', CustomAdapter())
