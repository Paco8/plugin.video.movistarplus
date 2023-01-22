# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import json
import requests

from .log import LOG, print_json

class Network(object):
  headers = {}
  session = requests.Session()

  def load_url(self, url, headers = None):
    if headers is None: headers = self.headers
    response = self.session.get(url, headers=headers, allow_redirects=True)
    content = response.content.decode('utf-8')
    return content

  def load_data(self, url, headers = None):
    content = self.load_url(url, headers)
    try:
      data = json.loads(content)
      return data
    except:
      return {'error': content}

  def post_data(self, url, data, headers = None):
    if headers is None: headers = self.headers
    #LOG('post_data: {}'.format(data))
    #print_json(headers)
    response = self.session.post(url, headers=headers, data=data)
    content = response.content.decode('utf-8')
    #LOG(content)
    data = json.loads(content)
    return data
