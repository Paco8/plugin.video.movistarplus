# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

import sys
import xbmc
import xbmcgui
import xbmcplugin
from .log import LOG
from .addon import addon

def handle():
  try:
    return int(sys.argv[1])
  except:
    return -1

def input_window(heading, text = '', hidden = False):
  res = None
  keyboard = xbmc.Keyboard(text)
  keyboard.setHeading(heading)
  keyboard.setHiddenInput(hidden)
  keyboard.doModal()
  if (keyboard.isConfirmed()):
    res = keyboard.getText()
  del keyboard
  return res

def open_folder(name, content_type = 'videos'):
  LOG('handle: {}'.format(handle()))
  xbmcplugin.setPluginCategory(handle(), name)
  xbmcplugin.setContent(handle(), content_type)

def close_folder(updateListing=False, cacheToDisc=True):
  xbmcplugin.endOfDirectory(handle(), updateListing=updateListing, cacheToDisc=cacheToDisc)

def add_menu_option(title, url, context_menu = None, info = None, art = None):
  list_item = xbmcgui.ListItem(label=title)
  if not info:
    info = {'title': title, 'plot': '[B][/B]'}
  if not art:
    art = {'icon': addon.getAddonInfo('icon'), 'poster': addon.getAddonInfo('icon')}
  list_item.setInfo('video', info)
  list_item.setArt(art)
  if context_menu:
    list_item.addContextMenuItems(context_menu)
  xbmcplugin.addDirectoryItem(handle(), url, list_item, True)

def show_notification(message, icon = xbmcgui.NOTIFICATION_ERROR):
  if icon == xbmcgui.NOTIFICATION_ERROR:
    heading = addon.getLocalizedString(30200)
  else:
    heading = addon.getLocalizedString(30201)
    icon = addon.getAddonInfo('icon')
  xbmcgui.Dialog().notification(heading, message, icon, 5000)
