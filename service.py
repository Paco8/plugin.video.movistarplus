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
  from resources.lib.gui import show_notification

  def needs_update(filename):
    if os.path.exists(filename):
      file_modification_time = datetime.fromtimestamp(os.path.getmtime(filename))
      return datetime.now() - file_modification_time > timedelta(hours=6)
    return True

  folder = addon.getSetting('epg_folder')
  if sys.version_info[0] > 2:
    folder = bytes(folder, 'utf-8')
  LOG('folder for channels and epg: {}'.format(folder))
  if not folder or not os.path.isdir(folder): return

  channels_filename = os.path.join(folder, b"movistar-channels.m3u8")
  epg_filename = os.path.join(folder, b"movistar-epg.xml")
  LOG('channels filename: {}'.format(channels_filename))
  LOG('epg filename: {}'.format(epg_filename))

  channels_needs_update = needs_update(channels_filename)
  epg_needs_update = needs_update(epg_filename)
  LOG('channels_needs_update: {} epg_needs_update: {}'.format(channels_needs_update, epg_needs_update))

  if channels_needs_update or epg_needs_update:
    from resources.lib.movistar import Movistar
    reuse_devices = addon.getSettingBool('reuse_devices')
    m = Movistar(profile_dir, reuse_devices)
    if not m.logged: return
    if channels_needs_update:
      show_notification(addon.getLocalizedString(30310), xbmcgui.NOTIFICATION_INFO)
      m.export_channels_to_m3u8(channels_filename)
    if epg_needs_update:
      show_notification(addon.getLocalizedString(30311), xbmcgui.NOTIFICATION_INFO)
      m.export_epg_to_xml(epg_filename)

if __name__ == '__main__':
  LOG('Service started')
  proxy = Proxy()
  proxy.start()
  LOG('proxy_address: {}'.format(proxy.proxy_address))
  cache = Cache(profile_dir)
  cache.save_file('proxy.conf', proxy.proxy_address)

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
