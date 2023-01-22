# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import json

def LOG(message):
  try:
    import xbmc
    import xbmcaddon
    xbmc.log('[{}] {}'.format(xbmcaddon.Addon().getAddonInfo('id'), message), xbmc.LOGDEBUG)
  except:
    print(message)

def print_json(data):
  LOG(json.dumps(data, indent=4))
