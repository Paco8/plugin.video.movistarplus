#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import xbmc
import xbmcgui
from resources.lib.proxy import Proxy
from resources.lib.addon import *
from resources.lib.log import LOG
from resources.lib.cache import Cache

def export_epg():
  from datetime import datetime, timedelta

  def needs_update(filename):
    if os.path.exists(filename):
      file_modification_time = datetime.fromtimestamp(os.path.getmtime(filename))
      return datetime.now() - file_modification_time > timedelta(hours=6)
    return True

  channels_filename = os.path.join(profile_dir, 'channels.m3u8')
  epg_filename = os.path.join(profile_dir, 'epg.xml')
  LOG('channels filename: {}'.format(channels_filename))
  LOG('epg filename: {}'.format(epg_filename))

  channels_needs_update = needs_update(channels_filename)
  epg_needs_update = needs_update(epg_filename)
  LOG('channels_needs_update: {} epg_needs_update: {}'.format(channels_needs_update, epg_needs_update))

  if channels_needs_update or epg_needs_update:
    xbmc.executebuiltin('RunPlugin(plugin://plugin.video.movistarplus/?action=export_epg_now)')

if __name__ == '__main__':
  LOG('Service started')
  proxy = Proxy()
  proxy.start()
  LOG('proxy_address: {}'.format(proxy.proxy_address))
  cache = Cache(profile_dir)
  cache.save_file('proxy.txt', proxy.proxy_address)

  if addon.getSettingBool('export_epg'):
    try:
      export_epg()
    except:
      pass

  monitor = xbmc.Monitor()
  while not monitor.abortRequested():
    if monitor.waitForAbort(1):
      break

  proxy.stop()
