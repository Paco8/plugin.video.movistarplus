# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import sys
import json

import xbmc
import xbmcgui
import xbmcplugin

if sys.version_info[0] >= 3:
  import urllib.request as urllib2
  from urllib.parse import urlencode, parse_qsl, quote_plus
  unicode = str
else:
  import urllib2
  from urllib import urlencode, quote_plus
  from urlparse import parse_qsl

import xbmcaddon
import os.path

from .log import LOG
from .movistar import *
from .addon import *
from .gui import *

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

try:  # Kodi >= 19
  from xbmcvfs import translatePath
except ImportError:  # Kodi 18
  from xbmc import translatePath


def get_url(**kwargs):
  return '{0}?{1}'.format(_url, urlencode(kwargs))

def play(params):
  LOG('play - params: {}'.format(params))

  if not 'url' in params: return

  url = params['url']
  channel_id = params['id']
  stype = params['stype']

  token = m.account['ssp_token']
  session_token = m.account['session_token']

  import inputstreamhelper
  is_helper = inputstreamhelper.Helper('mpd', drm='com.widevine.alpha')
  if not is_helper.check_inputstream():
    show_notification(addon.getLocalizedString(30202))
    return

  """
  if addon.getSettingBool('reregister'):
    m.unregister_device()
    m.register_device()
  """

  if addon.getSettingBool('open_session') or stype == 'vod':
    d = m.open_session(params['session_request'], session_token)
    LOG('Open session: d: {}'.format(d))
    if d['resultCode'] != 0:
      dialog = xbmcgui.Dialog().notification('Error', d['resultText'], xbmcgui.NOTIFICATION_ERROR, 5000)
      return
    if 'resultData' in d and 'cToken' in d['resultData']:
      token = d['resultData']['cToken']

    if not addon.getSettingBool('open_session'):
      d = m.delete_session()
      LOG('Delete session: d: {}'.format(d))

  LOG("*** TEST token: {} session_token: {}".format(token, session_token))

  #url = 'https://vamos-nmp-movistarplus.emisiondof6.com/hls/vamos.isml/index-02-spa.m3u8'

  if stype in ['u7d', 'rec']:
    d = m.get_u7d_url(url)
    url = d['url']

  proxy = m.cache.load_file('proxy.conf')
  if addon.getSettingBool('manifest_modification') and proxy:
    url = '{}/?manifest={}'.format(proxy, url)

  LOG("*** TEST url: {}".format(url))

  headers = 'Content-Type=application/octet-stream'
  headers += '&User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
  headers += '&Accept=*/*&Accept-Language=es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
  headers += '&Referer=https://ver.movistarplus.es/'
  headers += '&Origin=https://ver.movistarplus.es&Connection=keep-alive'
  headers += '&Host=wv-ottlic-f3.imagenio.telefonica.net'

  license_url = 'https://wv-ottlic-f3.imagenio.telefonica.net/TFAESP/wvls/contentlicenseservice/v1/licenses'
  certificate = (
     'CsECCAMSEBcFuRfMEgSGiwYzOi93KowYgrSCkgUijgIwggEKAoIBAQCZ7Vs7Mn2rXiTvw7YqlbWY'
     'UgrVvMs3UD4GRbgU2Ha430BRBEGtjOOtsRu4jE5yWl5KngeVKR1YWEAjp+GvDjipEnk5MAhhC28V'
     'jIeMfiG/+/7qd+EBnh5XgeikX0YmPRTmDoBYqGB63OBPrIRXsTeo1nzN6zNwXZg6IftO7L1KEMpH'
     'SQykfqpdQ4IY3brxyt4zkvE9b/tkQv0x4b9AsMYE0cS6TJUgpL+X7r1gkpr87vVbuvVk4tDnbNfF'
     'XHOggrmWEguDWe3OJHBwgmgNb2fG2CxKxfMTRJCnTuw3r0svAQxZ6ChD4lgvC2ufXbD8Xm7fZPvT'
     'CLRxG88SUAGcn1oJAgMBAAE6FGxpY2Vuc2Uud2lkZXZpbmUuY29tEoADrjRzFLWoNSl/JxOI+3u4'
     'y1J30kmCPN3R2jC5MzlRHrPMveoEuUS5J8EhNG79verJ1BORfm7BdqEEOEYKUDvBlSubpOTOD8S/'
     'wgqYCKqvS/zRnB3PzfV0zKwo0bQQQWz53ogEMBy9szTK/NDUCXhCOmQuVGE98K/PlspKkknYVeQr'
     'OnA+8XZ/apvTbWv4K+drvwy6T95Z0qvMdv62Qke4XEMfvKUiZrYZ/DaXlUP8qcu9u/r6DhpV51Wj'
     'x7zmVflkb1gquc9wqgi5efhn9joLK3/bNixbxOzVVdhbyqnFk8ODyFfUnaq3fkC3hR3f0kmYgI41'
     'sljnXXjqwMoW9wRzBMINk+3k6P8cbxfmJD4/Paj8FwmHDsRfuoI6Jj8M76H3CTsZCZKDJjM3BQQ6'
     'Kb2m+bQ0LMjfVDyxoRgvfF//M/EEkPrKWyU2C3YBXpxaBquO4C8A0ujVmGEEqsxN1HX9lu6c5OMm'
     '8huDxwWFd7OHMs3avGpr7RP7DUnTikXrh6X0')

  play_item = xbmcgui.ListItem(path= url)
  play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
  #play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
  if format(addon.getSetting('drm_type')) == 'Playready':
    play_item.setProperty('inputstream.adaptive.license_type', 'com.microsoft.playready')
  else:
    play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')

  if addon.getSettingBool('use_proxy_for_license') and proxy:
    request_id = str(int(time.time()*1000))
    license_url = '{}/license?token={}&stype={}&session_request={}&session_token={}&request_id={}||R{{SSM}}|'.format(proxy, quote_plus(token), stype, quote_plus(params['session_request']), quote_plus(session_token), request_id)
    LOG('license_url: {}'.format(license_url))
    play_item.setProperty('inputstream.adaptive.license_key', license_url)
  else:
    play_item.setProperty('inputstream.adaptive.license_key', '{}|{}&nv-authorizations={}|R{{SSM}}|'.format(license_url, headers, token))
  play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0')
  play_item.setProperty('inputstream.adaptive.server_certificate', certificate)
  #play_item.setProperty('inputstream.adaptive.license_flags', 'persistent_storage')
  #play_item.setProperty('inputstream.adaptive.license_flags', 'force_secure_decoder')

  if sys.version_info[0] < 3:
    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
  else:
    play_item.setProperty('inputstream', 'inputstream.adaptive')

  play_item.setMimeType('application/dash+xml')
  play_item.setContentLookup(False)

  # Subtitles
  if stype == 'vod' and addon.getSettingBool('use_ttml2ssa'):
    # Convert subtitles
    from ttml2ssa import Ttml2SsaAddon
    ttml = Ttml2SsaAddon()
    #ttml.use_language_filter = False
    subtype = ttml.subtitle_type()

    subfolder = profile_dir + os.sep +'subtitles/'
    if not os.path.exists(subfolder):
      os.makedirs(subfolder)

    sublist = m.get_subtitles(url)
    LOG('sublist: {}'.format(sublist))
    subpaths = []
    for sub in sublist:
      filename =  subfolder + sub['lang']
      LOG('Converting {}'.format(sub['filename']))
      response = m.net.session.get(sub['url'], allow_redirects=True)
      content = response.content
      with io.open(filename + '.ttml', 'w', encoding='utf-8', newline='') as handle:
        handle.write(content.decode('utf-8'))
      ttml.parse_ttml_from_string(content)
      if subtype != 'srt':
        filename_ssa = filename + '.ssa'
        ttml.write2file(filename_ssa)
        subpaths.append(filename_ssa)
      if subtype != 'ssa':
        filename_srt = filename
        if (subtype == 'both'): filename_srt += '.SRT'
        filename_srt += '.srt'
        ttml.write2file(filename_srt)
        subpaths.append(filename_srt)
    play_item.setSubtitles(subpaths)

  xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

  player.running = True
  monitor = xbmc.Monitor()
  while not monitor.abortRequested() and player.running:
    if monitor.waitForAbort(1):
      break
  LOG('Exiting play')


def add_videos(category, ctype, videos, ref=None, url_next=None, url_prev=None):
  #LOG("*** TEST category: {} ctype: {}".format(category, ctype))
  xbmcplugin.setPluginCategory(_handle, category)
  xbmcplugin.setContent(_handle, ctype)

  if ctype == 'movies' or ctype == 'seasons':
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LASTPLAYED)
  if ctype == 'episodes':
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_EPISODE)

  """
  if url_prev:
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(30110)) # Previous page
    xbmcplugin.addDirectoryItem(_handle, get_url(action=ref, url=url_prev, name=category), list_item, True)
  """

  for t in videos:
    #LOG("*** TEST t: {}".format(t))
    if 'subscribed' in t:
      if addon.getSettingBool('only_subscribed') and t['subscribed'] == False: continue
      t['info']['title'] = m.colorize_title(t)
    title_name = t['info']['title'].encode('utf-8')
    if not 'type' in t: continue
    if t['type'] == 'movie':
      list_item = xbmcgui.ListItem(label = title_name)
      #if t['stream_type'] == 'tv':
      #  action = get_url(action='epg', id=t['id'], name=t['name'].encode('utf-8'))
      #  LOG('action: {}'.format(action))
      #  list_item.addContextMenuItems([('EPG', "RunPlugin(" + action + ")")])
      if t['url'] == '':
         t['info']['title'] = '[COLOR gray]' + t['info']['title'] +'[/COLOR]'
      list_item.setProperty('IsPlayable', 'true')
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])
      url = get_url(action='play', id=t['id'], url=t['url'], session_request=t['session_request'], stype=t['stream_type'])
      xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    elif t['type'] == 'series':
      list_item = xbmcgui.ListItem(label = title_name)
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='series', id=t['id'], name=title_name), list_item, True)
    elif t['type'] == 'season':
      list_item = xbmcgui.ListItem(label = title_name)
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='season', id=t['id'], name=title_name), list_item, True)
    elif t['type'] == 'category':
      list_item = xbmcgui.ListItem(label = title_name)
      #list_item.setInfo('video', t['info'])
      #list_item.setArt(t['art'])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='category', id=t['id'], name=title_name), list_item, True)

  if url_next:
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(30109)) # Next page
    xbmcplugin.addDirectoryItem(_handle, get_url(action=ref, url=url_next, name=category), list_item, True)

  xbmcplugin.endOfDirectory(_handle)

def list_devices(params):
  LOG('list_devices: params: {}'.format(params))

  devices = m.get_devices(False)

  if 'id' in params:
    if params['name'] == 'select':
      LOG('Selecting device {}'.format(params['id']))
      m.change_device(params['id'])
    elif params['name'] == 'close':
      LOG('Closing session {}'.format(params['id']))
      m.delete_session(params['id'])
    elif params['name'] == 'delete':
      LOG('Removing device {}'.format(params['id']))
      m.delete_device(params['id'])
      if params['id'] == m.account['device_id']:
        LOG('Registering device')
        m.register_device()

    xbmc.executebuiltin("Container.Refresh")
    return

  open_folder(addon.getLocalizedString(30108)) # Devices

  for d in devices:
    name = d['name'] +' - '+ d['type'] + ' (' + d['reg_date'] + ')'
    if d['playing']: name += ' [' + d['playing'] + ']'
    name += ' ['+ d['id'][:5] +']'
    if d['id'] == m.account['device_id']:
      name = '[B][COLOR blue]' + name + '[/COLOR][/B]'

    select_action = get_url(action='devices', id=d['id'], name='select')
    close_action = get_url(action='devices', id=d['id'], name='close')
    remove_action = get_url(action='devices', id=d['id'], name='delete')
    cm = [(addon.getLocalizedString(30150), "RunPlugin(" + close_action + ")"),
          (addon.getLocalizedString(30151), "RunPlugin(" + remove_action + ")")]
    if d['type_code'] == 'WP':
      cm.insert(0, (addon.getLocalizedString(30152), "RunPlugin(" + select_action + ")"))
      default_action = select_action
    else:
      default_action = close_action
    add_menu_option(name, default_action, cm)

  close_folder(cacheToDisc=False)

def list_profiles(params):
  LOG('list_profiles: params: {}'.format(params))

  profiles = m.get_profiles()

  if 'id' in params:
    if params['name'] == 'select':
      LOG('Selecting profile {}'.format(params['id']))
      m.change_profile(params['id'])
    xbmc.executebuiltin("Container.Refresh")
    return

  open_folder(addon.getLocalizedString(30180)) # Profiles
  for p in profiles:
    name = p['name']
    if p['id'] == m.account['profile_id']:
      name = '[B][COLOR blue]' + name + '[/COLOR][/B]'
    select_action = get_url(action='profiles', id=p['id'], name='select')
    add_menu_option(name, select_action)
  close_folder(cacheToDisc=False)

def list_epg(params):
  LOG('list_epg: {}'.format(params))
  if 'id' in params:
    epg = m.get_epg()
    xbmcplugin.setPluginCategory(_handle, params['name'])
    xbmcplugin.setContent(_handle, 'files')
    for p in epg[params['id']]:
      name = '[B]' + p['start_str'] + '[/B] ' + p['desc1']
      if p['desc2']: name += ' - '+ p['desc2']
      plot = name +"\n" + p['desc2']
      list_item = xbmcgui.ListItem(label=name)
      list_item.setInfo('video', {'name':name, 'plot':plot})
      xbmcplugin.addDirectoryItem(_handle, '', list_item, False)
    xbmcplugin.endOfDirectory(_handle)
  else:
    channels = m.get_channels()
    open_folder(addon.getLocalizedString(30107)) # EPG
    for t in channels:
      name = t['info']['title']
      add_menu_option(name, get_url(action='epg', id=t['id'], name=name.encode('utf-8')), art=t['art'])
    close_folder()

def listing(name, url):
  data = m.download_list(url, use_hz=False)
  l = m.get_list(data['Contenidos'])
  url_next = data['next']['href'] if isinstance(data['next'], dict) and 'href' in data['next'] else None
  url_prev = data['prev']['href'] if isinstance(data['next'], dict) and 'prev' in data['next'] else None
  add_videos(name, 'movies', l, url_next=url_next, url_prev=url_prev, ref='listing')

def listing_hz(name, url):
  data = m.download_list(url, use_hz=True)
  l = m.get_list(data['Contenidos'])
  url_next = data['next']['href'] if isinstance(data['next'], dict) and 'href' in data['next'] else None
  url_prev = data['prev']['href'] if isinstance(data['next'], dict) and 'prev' in data['next'] else None
  add_videos(name, 'movies', l, url_next=url_next, url_prev=url_prev, ref='listing_hz')

def list_vod():
  open_folder(addon.getLocalizedString(30111)) # VOD
  name = addon.getLocalizedString(30105).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='movies'))) # Movies

  name = addon.getLocalizedString(30106).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='tvshows'))) # TV Shows

  name = addon.getLocalizedString(30120).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='documentaries'))) # Documentaries

  name = addon.getLocalizedString(30121).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='kids'))) # Kids
  close_folder()

def login_with_key():
  filename = xbmcgui.Dialog().browseSingle(1, addon.getLocalizedString(30182), '', '.key')
  if filename:
    m.install_key_file(filename)
    m.cache.remove_file('access_token.conf')
    m.cache.remove_file('account.json')
    m.cache.remove_file('device_id.conf')
    m.cache.remove_file('devices.json')
    m.cache.remove_file('profile_id.conf')
    m.cache.remove_file('tokens.json')

def router(paramstring):
  """
  Router function that calls other functions
  depending on the provided paramstring
  :param paramstring: URL encoded plugin paramstring
  :type paramstring: str
  """

  params = dict(parse_qsl(paramstring))
  LOG('params: {}'.format(params))
  if params:
    if params['action'] == 'play':
      play(params)
    elif params['action'] == 'tv':
      if addon.getSettingBool('channels_with_epg'):
        channels = m.get_channels_with_epg()
      else:
        channels = m.get_channels()
      add_videos(addon.getLocalizedString(30104), 'movies', channels)
    elif params['action'] == 'devices':
      list_devices(params)
    elif params['action'] == 'profiles':
      list_profiles(params)
    elif params['action'] == 'login_with_key':
      login_with_key()
    elif params['action'] == 'logout':
      pass
    elif params['action'] == 'epg':
      list_epg(params)
    elif params['action'] == 'wishlist':
      # Wishlist
      listing_hz(addon.getLocalizedString(30102), m.get_wishlist_url())
    elif params['action'] == 'recordings':
      # Recordings
      listing_hz(addon.getLocalizedString(30103), m.get_recordings_url())
    elif params['action'] == 'listing':
      listing(params['name'], params['url'])
    elif params['action'] == 'listing_hz':
      listing_hz(params['name'], params['url'])
    elif params['action'] == 'series':
      add_videos(params['name'], 'seasons', m.get_seasons(params['id']))
    elif params['action'] == 'season':
      add_videos(params['name'], 'episodes', m.get_episodes(params['id']))
    elif params['action'] == 'vod':
      list_vod()
  else:
    # Main
    open_folder(addon.getLocalizedString(30101)) # Menu
    xbmcplugin.setContent(_handle, 'files')

    if m.logged:
      add_menu_option(addon.getLocalizedString(30104), get_url(action='tv')) # TV
      add_menu_option(addon.getLocalizedString(30107), get_url(action='epg')) # EGP
      add_menu_option(addon.getLocalizedString(30102), get_url(action='wishlist')) # My list
      add_menu_option(addon.getLocalizedString(30103), get_url(action='recordings')) # Recordings
      add_menu_option(addon.getLocalizedString(30111), get_url(action='vod')) # VOD
      add_menu_option(addon.getLocalizedString(30180), get_url(action='profiles')) # Profiles
      add_menu_option(addon.getLocalizedString(30108), get_url(action='devices')) # Devices
      #add_menu_option(addon.getLocalizedString(30150), get_url(action='logout')) # Close session

    add_menu_option(addon.getLocalizedString(30181), get_url(action='login_with_key')) # Login with key
    close_folder(cacheToDisc=False)


class Player(xbmc.Player):
  running = False

  def onAVStarted(self):
    LOG('Playback started')

  def onPlayBackPaused(self):
    LOG('Playback paused')

  def onPlayBackResumed(self):
    LOG('Playback resumed')

  def onPlayBackEnded(self):
    LOG('Playback ended')
    self.close_session()

  def onPlayBackStopped(self):
    LOG('Playback stopped')
    self.close_session()

  def close_session(self):
    if self.running:
      LOG('Closing session')
      d = m.delete_session()
      LOG('delete_session: {}'.format(d))
      self.running = False

def run():
  global m
  reuse_devices = addon.getSettingBool('reuse_devices')
  LOG('profile_dir: {}'.format(profile_dir))
  LOG('reuse_devices: {}'.format(reuse_devices))
  m = Movistar(profile_dir, reuse_devices=reuse_devices)

  global player
  player = Player()

  # Call the router function and pass the plugin call parameters to it.
  # We use string slicing to trim the leading '?' from the plugin call paramstring
  router(sys.argv[2][1:])
