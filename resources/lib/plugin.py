# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import sys
import json
import io
import os.path

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

if sys.version_info[0] >= 3:
  import urllib.request as urllib2
  from urllib.parse import urlencode, parse_qsl, quote_plus
  unicode = str
else:
  import urllib2
  from urllib import urlencode, quote_plus
  from urlparse import parse_qsl

from .log import LOG
from .movistar import *
from .addon import *
from .gui import *
from .useragent import useragent

kodi_version= int(xbmc.getInfoLabel('System.BuildVersion')[:2])

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def get_url(**kwargs):
  for key, value in kwargs.items():
    if isinstance(value, unicode):
      kwargs[key] = value.encode('utf-8')
  return '{0}?{1}'.format(_url, urlencode(kwargs))

def play(params):
  LOG('play - params: {}'.format(params))

  if not 'url' in params:
    show_notification(addon.getLocalizedString(30204))
    return

  url = params['url']
  channel_id = params['id']
  stype = params['stype']

  token = m.account['ssp_token']

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

  session_opened = False
  if addon.getSettingBool('open_session') or stype == 'vod':
    d = m.open_session(params['session_request'])
    session_opened = True
    LOG('Open session: d: {}'.format(d))
    if d['resultCode'] != 0:
      show_notification(d['resultText'])
      return
    if 'resultData' in d and 'cToken' in d['resultData']:
      token = d['resultData']['cToken']

    if stype == 'vod':
      d = m.delete_session()
      session_opened = False
      LOG('Delete session: d: {}'.format(d))

  LOG("token: {}".format(token))

  if stype in ['u7d', 'rec']:
    d = m.get_u7d_url(url)
    if 'resultText' in d:
      show_notification(d['resultText'])
      return
    else:
      url = d['url']
      #if True:
      #  url = url.replace('DASH_WPC_WIDEVINE', 'DASH_TV_WIDEVINE')

  # U7D from start and end times
  if stype == 'tv' and all(param in params for param in ['cas_id', 'start_time', 'end_time']):
    from datetime import datetime
    start = datetime.utcfromtimestamp(int(params['start_time']))
    end = datetime.utcfromtimestamp(int(params['end_time']))
    catchup_url = 'https://stover-wp0.cdn.telefonica.com/{cas_id}/vxfmt=dp/Manifest.mpd?device_profile=DASH_TV_WIDEVINE&start_time={start_time}&end_time={end_time}'
    url = catchup_url.format(cas_id=params['cas_id'], start_time=start.strftime('%Y-%m-%dT%H:%M:%SZ'), end_time=end.strftime('%Y-%m-%dT%H:%M:%SZ'))
    LOG('url from capchup: {}'.format(url))


  # Read the proxy address
  proxy = addon.getSetting('proxy_address')
  LOG('proxy address: {}'.format(proxy))

  if addon.getSettingBool('manifest_modification') and proxy:
    url = '{}/?manifest={}'.format(proxy, url)

  LOG("url: {}".format(url))

  headers = 'Content-Type=application/octet-stream'
  headers += '&User-Agent=' + useragent
  headers += '&Accept=*/*&Accept-Language=es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
  headers += '&Referer=https://ver.movistarplus.es/'
  headers += '&Origin=https://ver.movistarplus.es'
  #headers += '&Host=wv-ottlic-f3.imagenio.telefonica.net'
  manifest_headers = 'User-Agent=' + useragent

  if True: #stype in ['tv', 'u7d', 'rec']:
    cdn_token = m.cache.load('cdn.conf')
    if not cdn_token:
      cdn_token = m.get_cdntoken()
      m.cache.save_file('cdn.conf', cdn_token)
    #LOG('cdn_token: {}'.format(cdn_token))
    manifest_headers += '&x-tcdn-token=' + cdn_token

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
    license_url = '{}/license?token={}&stype={}&session_request={}&request_id={}||R{{SSM}}|'.format(proxy, quote_plus(token), stype, quote_plus(params['session_request']), request_id)
    LOG('license_url: {}'.format(license_url))
    play_item.setProperty('inputstream.adaptive.license_key', license_url)
  else:
    play_item.setProperty('inputstream.adaptive.license_key', '{}|{}&nv-authorizations={}|R{{SSM}}|'.format(license_url, headers, token))

  play_item.setProperty('inputstream.adaptive.stream_headers', manifest_headers)
  play_item.setProperty('inputstream.adaptive.manifest_headers', manifest_headers)

  play_item.setProperty('inputstream.adaptive.server_certificate', certificate)
  #play_item.setProperty('inputstream.adaptive.license_flags', 'persistent_storage')
  #play_item.setProperty('inputstream.adaptive.license_flags', 'force_secure_decoder')

  if stype == 'u7d':
    play_item.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')

  if kodi_version < 19:
    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
  else:
    play_item.setProperty('inputstream', 'inputstream.adaptive')

  play_item.setMimeType('application/dash+xml')
  play_item.setContentLookup(False)

  # Add info
  if addon.getSettingBool('add_extra_info') and stype in ['vod', 'u7d', 'rec']:
    t = {'id': params['id']}
    if 'show_id' in params: t['show_id'] = params['show_id']
    m.add_video_extra_info(t)
    play_item.setInfo('video', t['info'])
    play_item.setArt(t['art'])

  # Subtitles
  if stype == 'vod' and addon.getSettingBool('use_ttml2ssa'):
    # Convert subtitles
    from ttml2ssa import Ttml2SsaAddon
    ttml = Ttml2SsaAddon()
    #ttml.use_language_filter = False
    subtype = ttml.subtitle_type()

    subfolder = os.path.join(profile_dir, 'subtitles')
    if not os.path.exists(subfolder):
      os.makedirs(subfolder)

    sublist = m.get_subtitles(params['url'])
    LOG('sublist: {}'.format(sublist))
    subpaths = []
    for sub in sublist:
      filename = os.path.join(subfolder, sub['lang'])
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

  #if True:
  #  m.unregister_device()
  #  m.register_device()

  xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

  LOG('**** session_opened: {}'.format(session_opened))
  is_sport_channel = (stype == 'tv' and channel_id in ['MLIGA', 'DAZNLI', 'MLIG1', 'CHAPIO', 'CHAP1', 'CHAP2', 'MLIGUH', 'CHAUHD', 'CHUHD1'])
  if session_opened or is_sport_channel:
    if is_sport_channel:
      last_time = 0 #time.time()
      window = xbmcgui.Window(12005)
      label = xbmcgui.ControlLabel(0, 0, 400, 20, m.account['id'], textColor='0xFFFFFFFF', alignment=6)
    from .player import MyPlayer
    player = MyPlayer()
    monitor = xbmc.Monitor()
    while not monitor.abortRequested() and player.running:
      monitor.waitForAbort(10)
      #LOG('**** waiting')
      if is_sport_channel and player.isPlaying():
        now = time.time()
        if now - last_time >= 15*60:
          last_time = now
          #show_notification(m.account['id'], xbmcgui.NOTIFICATION_INFO)
          w = window.getWidth()
          h = window.getHeight()
          #LOG('window h: {} w: {}'.format(h, w))
          pos_x = w-label.getWidth()-60
          pos_y = h-200
          label.setPosition(pos_x, pos_y)
          window.addControl(label)
          time.sleep(20)
          window.removeControl(label)
    if session_opened:
      d = m.delete_session()
      LOG('Delete session: d: {}'.format(d))
    LOG('Playback finished')


def add_videos(category, ctype, videos, ref=None, url_next=None, url_prev=None, from_wishlist=False):
  #LOG("category: {} ctype: {}".format(category, ctype))
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
    #LOG("t: {}".format(t))
    if 'subscribed' in t:
      if addon.getSettingBool('only_subscribed') and t['subscribed'] == False: continue
    t['info']['title'] = m.colorize_title(t)

    if 'availability' in t:
      ends = int(t['availability'].get('end', '0'))
      if ends > 0:
        now = int(time.time()*1000)
        n_hours = int((ends - now) / (1000 * 60 * 60))
        n_days = int(n_hours / 24)
        if (n_days <= addon.getSettingInt('expdays')):
          if n_days < 1:
            t['info']['title'] += ' [COLOR red](' + addon.getLocalizedString(30401).format(n_hours) + ')[/COLOR]'
          else:
            t['info']['title'] += ' [COLOR red](' + addon.getLocalizedString(30400).format(n_days) + ')[/COLOR]'

    title_name = t['info']['title']
    if not 'type' in t: continue

    wishlist_action = None
    if t['type'] in ['movie', 'series', 'season']:
      id = t['id']
      stype = 'vod'
      possible_to_add = False

      if from_wishlist:
        # Remove from wishlist
        if 'favorite_data' in t:
          if 'favorites2' in t['favorite_data']:
            id = t['favorite_data']['favorites2']['id']
            stype = t['favorite_data']['favorites2']['family']
            possible_to_add = True
          elif t['type'] == 'season' and 'favorites2.season' in t['favorite_data']:
            id = t['favorite_data']['favorites2.season']['id']
            stype = t['favorite_data']['favorites2.season']['family']
            possible_to_add = True
      else:
        # Add to wishlist
        if t['type'] in ['series', 'season']:
          possible_to_add = t.get('seguible', False)

        if t['type'] == 'movie':
          if t.get('stream_type') == 'vod':
            possible_to_add = t['url'] != ''
          if 'show_id' in t:
            possible_to_add = t['url'] != ''
            stype = 'tv'
            id = t['show_id']

      if possible_to_add:
        if not from_wishlist:
          op = 'add'
          message = 30175
        else:
          op = 'delete'
          message = 30176
        wishlist_action = (addon.getLocalizedString(message), "RunPlugin(" + get_url(action='to_wishlist', id=id, op=op, stype=stype) + ")")

    if t['type'] == 'movie':
      list_item = xbmcgui.ListItem(label = title_name)
      #if t['url'] == '':
      #   t['info']['title'] = '[COLOR gray]' + t['info']['title'] +'[/COLOR]'
      list_item.setProperty('IsPlayable', 'true')
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])

      actions = []
      if t.get('stream_type') == 'u7d':
        #LOG(t)
        if 'show_id' in t and not t.get('aired', False):
          record_program_action = (addon.getLocalizedString(30171), "RunPlugin(" + get_url(action='add_recording', id=t['show_id']) + ")")
          actions.append(record_program_action)
        if 'serie_id' in t:
          record_season_action = (addon.getLocalizedString(30169), "RunPlugin(" + get_url(action='add_recording_season', id=t['serie_id']) + ")")
          actions.append(record_season_action)

      if 'rec' in t:
        action = get_url(action='delete_recording', id=t['rec']['id'], name=t['rec']['name'])
        actions.append((addon.getLocalizedString(30173), "RunPlugin(" + action + ")"))

      if wishlist_action:
        actions.append(wishlist_action)

      if len(actions) > 0:
        #LOG(actions)
        list_item.addContextMenuItems(actions)

      url = get_url(action='play', id=t['id'], url=t['url'], session_request=t['session_request'], stype=t['stream_type'])
      if 'show_id' in t: url += '&show_id={}'.format(t['show_id'])
      xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    elif t['type'] == 'series':
      list_item = xbmcgui.ListItem(label = title_name)
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])
      if wishlist_action:
        list_item.addContextMenuItems([wishlist_action])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='series', id=t['id'], name=title_name), list_item, True)
    elif t['type'] == 'season':
      list_item = xbmcgui.ListItem(label = title_name)
      list_item.setInfo('video', t['info'])
      list_item.setArt(t['art'])
      if wishlist_action:
        list_item.addContextMenuItems([wishlist_action])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='season', id=t['id'], name=title_name), list_item, True)
    elif t['type'] == 'category':
      list_item = xbmcgui.ListItem(label = title_name)
      #list_item.setInfo('video', t['info'])
      #list_item.setArt(t['art'])
      xbmcplugin.addDirectoryItem(_handle, get_url(action='category', id=t['id'], name=title_name), list_item, True)

  if url_next:
    list_item = xbmcgui.ListItem(label = addon.getLocalizedString(30109)) # Next page
    xbmcplugin.addDirectoryItem(_handle, get_url(action=ref, url=url_next, from_wishlist=from_wishlist, name=category), list_item, True)

  xbmcplugin.endOfDirectory(_handle)

def list_devices(params):
  LOG('list_devices: params: {}'.format(params))

  devices = m.get_devices()

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
    img_url = m.get_profile_image_url(p['image_id'])
    art = {'icon': img_url} if img_url else None
    select_action = get_url(action='profiles', id=p['id'], name='select')
    add_menu_option(name, select_action, art=art)
  close_folder(cacheToDisc=False)

def list_epg(params):
  LOG('list_epg: {}'.format(params))
  from datetime import datetime, timedelta
  from .timeconv import my_strftime
  if 'id' in params:
    if not 'date' in params:
      today = datetime.today()
      for i in range(6, 0, -1):
        past_date = today - timedelta(days=i)
        date = past_date.strftime('%Y-%m-%dT00:00:00')
        display_str = my_strftime(past_date, '%a %d')
        add_menu_option(display_str, get_url(action='epg', id=params['id'], name=params['name'], date=date))
    add_videos(params['name'], 'movies', m.epg_to_movies(params['id'], params.get('date'), duration=1))
  else:
    channels = m.get_channels()
    open_folder(addon.getLocalizedString(30107)) # EPG
    for t in channels:
      name = t['info']['title']
      add_menu_option(name, get_url(action='epg', id=t['id'], name=name.encode('utf-8')), art=t['art'])
    close_folder()

def listing(name, url):
  data = m.download_list(url, use_hz=False)
  l = []
  url_next = None
  url_prev = None
  if 'Contenidos' in data:
    l = m.get_list(data['Contenidos'])
    url_next = data['next']['href'] if isinstance(data['next'], dict) and 'href' in data['next'] else None
    url_prev = data['prev']['href'] if isinstance(data['next'], dict) and 'prev' in data['next'] else None
  add_videos(name, 'movies', l, url_next=url_next, url_prev=url_prev, ref='listing')

def listing_hz(name, url, from_wishlist=False):
  data = m.download_list(url, use_hz=True)
  l = []
  url_next = None
  url_prev = None
  if 'Contenidos' in data:
    l = m.get_list(data['Contenidos'])
    url_next = data['next']['href'] if isinstance(data['next'], dict) and 'href' in data['next'] else None
    url_prev = data['prev']['href'] if isinstance(data['next'], dict) and 'prev' in data['next'] else None
  add_videos(name, 'movies', l, url_next=url_next, url_prev=url_prev, ref='listing_hz', from_wishlist=from_wishlist)

def list_vod0():
  open_folder(addon.getLocalizedString(30111)) # VOD
  name = addon.getLocalizedString(30105).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='movies'))) # Movies

  name = addon.getLocalizedString(30106).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='tvshows'))) # TV Shows

  name = addon.getLocalizedString(30120).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='documentaries'))) # Documentaries

  name = addon.getLocalizedString(30121).encode('utf-8')
  add_menu_option(name, get_url(action='listing', name=name, url=m.get_vod_list_url(cat='kids'))) # Kids

  sections = m.get_vod_sections()

  close_folder()

def list_vod():
  open_folder(addon.getLocalizedString(30111)) # VOD

  sections = m.get_vod_sections()
  for key, s in sections.items():
    if not s['visible']: continue
    name = s['name'].encode('utf-8')
    add_menu_option(name, get_url(action='list_section', name=name, key=key))

  close_folder()

def list_section(key):
  open_folder(addon.getLocalizedString(30111)) # VOD

  sections = m.get_vod_sections()
  items = sections[key]['data']
  for item in items:
    name = item['name'].encode('utf-8')
    add_menu_option(name, get_url(action='listing', name=name, url=item['url']))

  close_folder()

def search(params):
  search_term = params.get('search_term', None)
  if search_term:
    if sys.version_info[0] < 3:
      search_term = search_term.decode('utf-8')
    if params.get('name', None) == 'delete':
      m.delete_search(search_term)
      xbmc.executebuiltin("Container.Refresh")
    else:
      url = m.get_search_url(search_term)
      listing_hz(addon.getLocalizedString(30117), url)
    return

  if params.get('name', None) == 'new':
    search_term = input_window(addon.getLocalizedString(30116)) # Search term
    if search_term:
      if sys.version_info[0] < 3:
        search_term = search_term.decode('utf-8')
      m.add_search(search_term)
    xbmc.executebuiltin("Container.Refresh")
    return

  open_folder(addon.getLocalizedString(30113)) # Search
  add_menu_option(addon.getLocalizedString(30113), get_url(action='search', name='new')) # New search

  for i in reversed(m.search_list):
    remove_action = get_url(action='search', search_term=i, name='delete')
    cm = [(addon.getLocalizedString(30114), "RunPlugin(" + remove_action + ")")]
    add_menu_option(i.encode('utf-8'), get_url(action='search', search_term=i), cm)

  close_folder(cacheToDisc=False)

def order_recording(program_id):
  data = m.order_recording(program_id)
  if data and 'resultText' in data:
    show_notification(data['resultText'])
  else:
    show_notification(addon.getLocalizedString(30172), xbmcgui.NOTIFICATION_INFO)

def order_recording_season(season_id):
  data = m.order_recording_season(season_id)
  if data and 'resultText' in data:
    show_notification(data['resultText'])
  else:
    show_notification(addon.getLocalizedString(30172), xbmcgui.NOTIFICATION_INFO)

def delete_recording(id, name):
  if sys.version_info[0] < 3:
    name = name.decode('utf-8')
  res = xbmcgui.Dialog().yesno(addon.getLocalizedString(30173), addon.getLocalizedString(30174).format(name))
  if res == True:
    m.delete_recording(id)
    xbmc.executebuiltin("Container.Refresh")

def clear_session():
  m.delete_session_files()

def logout():
  clear_session()
  m.cache.remove_file('auth.key')

def login():
  def ask_credentials(username='', password=''):
    username = input_window(addon.getLocalizedString(30163), username) # Username
    if username:
      password = input_window(addon.getLocalizedString(30164), password, hidden=True) # Password
      if password:
        return username, password
    return None, None

  store_credentials = addon.getSettingBool('store_credentials')
  if store_credentials:
    username, password = m.load_credentials()
  else:
    username, password = ('', '')

  username, password = ask_credentials(username, password)
  if username:
    if store_credentials:
      m.save_credentials(username, password)
    success, _ = m.login(username, password)
    if success:
      clear_session()
    else:
      show_notification(addon.getLocalizedString(30166)) # Failed

def login_with_key():
  filename = xbmcgui.Dialog().browseSingle(1, addon.getLocalizedString(30182), '', '.key')
  if filename:
    m.install_key_file(filename)
    clear_session()

def export_key():
  directory = xbmcgui.Dialog().browseSingle(0, addon.getLocalizedString(30185), '')
  if directory:
    m.export_key_file(directory + 'movistarplus.key')

def import_credentials():
  filename = xbmcgui.Dialog().browseSingle(1, addon.getLocalizedString(30193), '', '.json')
  if filename:
    m.import_credentials(filename)

def export_credentials():
  directory = xbmcgui.Dialog().browseSingle(0, addon.getLocalizedString(30194), '')
  if directory:
    m.export_credentials(os.path.join(directory, 'credenciales.json'))

def select_account(id, name):
  m.switch_account(id)
  open_folder(name)
  add_menu_option(addon.getLocalizedString(30183), get_url(action='login')) # Login with username
  if addon.getSettingBool('enable_key_login'):
    add_menu_option(addon.getLocalizedString(30181), get_url(action='login_with_key')) # Login with key
    if os.path.exists(os.path.join(m.cache.config_directory, 'auth.key')):
      add_menu_option(addon.getLocalizedString(30184), get_url(action='export_key')) # Export key
  add_menu_option(addon.getLocalizedString(30150), get_url(action='logout')) # Close session
  add_menu_option(addon.getLocalizedString(30196), get_url(action='import_credentials'))
  if os.path.exists(os.path.join(m.cache.config_directory, 'credentials.json')):
    add_menu_option(addon.getLocalizedString(30195), get_url(action='export_credentials'))
  close_folder(cacheToDisc=False)

def list_accounts(params):
  LOG('list_accounts: {}'.format(params))

  if params.get('name') == 'new_account':
    m.create_new_account()

  accounts = m.get_accounts()
  open_folder(addon.getLocalizedString(30160)) # Accounts
  for account in accounts:
    name = account['name']
    login = account.get('login')
    if login:
      name += ' ({})'.format(login)
    if account['id'] == m.account_dir:
      display_name = '[B][COLOR blue]' + name + '[/COLOR][/B]'
    else:
      display_name = name
    add_menu_option(display_name, get_url(action='select_account', id=account['id'], name=name))
  add_menu_option(addon.getLocalizedString(30161), get_url(action='accounts', name='new_account')) # Add new
  close_folder(cacheToDisc=False)

  if params.get('name') == 'new_account':
    xbmc.executebuiltin('Container.Update({},replace)'.format(xbmc.getInfoLabel('Container.FolderPath')))

def iptv(params):
  LOG('iptv: params: {}'.format(params))
  if m.logged:
    #try:
    if True:
      from .iptvmanager import IPTVManager
      port = int(params['port'])
      if params['action'] == 'iptv-channels':
        IPTVManager(port).send_channels(m)
      elif params['action'] == 'iptv-epg':
        IPTVManager(port).send_epg(m)
    #except:
    #  pass

def create_iptv_settings():
  from .iptv import save_iptv_settings
  show_notification(addon.getLocalizedString(30319), xbmcgui.NOTIFICATION_INFO)
  output_file = 'instance-settings-91.xml' if kodi_version > 19 else 'settings.xml'
  epg_url = None
  if addon.getSettingBool('use_external_epg'):
    epg_url = addon.getSetting('epg_url')
  try:
    pvr_addon = xbmcaddon.Addon('pvr.iptvsimple')
    pvr_dir = translatePath(pvr_addon.getAddonInfo('profile'))
    LOG('pvr_dir: {}'.format(pvr_dir))
    filename = os.path.join(pvr_dir, output_file)
    if os.path.exists(filename):
      res = xbmcgui.Dialog().yesno(addon.getLocalizedString(30322), addon.getLocalizedString(30323))
      if res == False: return
    save_iptv_settings(filename, 'Movistarplus', 'movistarplus', epg_url)
    export_epg_now()
  except:
    show_notification(addon.getLocalizedString(30324))

def export_epg_now():
  def report_progress(message):
    show_notification(addon.getLocalizedString(30314).format(message), xbmcgui.NOTIFICATION_INFO)

  if not m.logged: return

  only_subscribed = addon.getSettingBool('only_subscribed')
  channels_filename = os.path.join(profile_dir, 'channels.m3u8')
  epg_filename = os.path.join(profile_dir, 'epg.xml')
  show_notification(addon.getLocalizedString(30310), xbmcgui.NOTIFICATION_INFO)
  m.export_channels_to_m3u8(channels_filename, only_subscribed)

  if not addon.getSettingBool('use_external_epg'):
    show_notification(addon.getLocalizedString(30311), xbmcgui.NOTIFICATION_INFO)
    m.export_epg_to_xml(epg_filename, addon.getSettingInt('export_days'), report_progress, only_subscribed)

  show_notification(addon.getLocalizedString(30313), xbmcgui.NOTIFICATION_INFO)


def to_wishlist(params):
  stype = params['stype']
  if params['op'] == 'add':
    retcode, message = m.add_to_wishlist(params['id'], stype)
  else:
    retcode, message = m.delete_from_wishlist(params['id'], stype)
  if retcode in [201, 204]:
    message = 30177 if params['op'] == 'add' else 30178
    show_notification(addon.getLocalizedString(message), xbmcgui.NOTIFICATION_INFO)
    if params['op'] == 'delete':
      xbmc.executebuiltin("Container.Refresh")
  else:
    show_notification(str(retcode) +': '+ message)


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
    elif params['action'] == 'login':
      login()
    elif params['action'] == 'export_key':
      export_key()
    elif params['action'] == 'export_credentials':
      export_credentials()
    elif params['action'] == 'import_credentials':
      import_credentials()
    elif params['action'] == 'select_account':
      select_account(params['id'], params['name'])
    elif params['action'] == 'accounts':
      list_accounts(params)
    elif params['action'] == 'logout':
      logout()
    elif params['action'] == 'epg':
      list_epg(params)
    elif params['action'] == 'add_recording':
      order_recording(params['id'])
    elif params['action'] == 'delete_recording':
      delete_recording(params['id'], params['name'])
    elif params['action'] == 'add_recording_season':
      order_recording_season(params['id'])
    elif params['action'] == 'wishlist':
      # Wishlist
      listing_hz(addon.getLocalizedString(30102), m.get_wishlist_url(), from_wishlist=True)
    elif params['action'] == 'continue-watching':
      listing_hz(addon.getLocalizedString(30102), m.get_viewings_url())
    elif params['action'] == 'recordings':
      # Recordings
      listing_hz(addon.getLocalizedString(30103), m.get_recordings_url())
    elif params['action'] == 'listing':
      listing(params['name'], params['url'])
    elif params['action'] == 'listing_hz':
      listing_hz(params['name'], params['url'], params.get('from_wishlist'))
    elif params['action'] == 'series':
      add_videos(params['name'], 'seasons', m.get_seasons(params['id']))
    elif params['action'] == 'season':
      add_videos(params['name'], 'episodes', m.get_episodes(params['id']))
    elif params['action'] == 'vod':
      list_vod()
    elif params['action'] == 'list_section':
      list_section(params['key'])
    elif params['action'] == 'search':
      search(params)
    elif params['action'] == 'create_iptv_settings':
      create_iptv_settings()
    elif params['action'] == 'export_epg_now':
      export_epg_now()
    elif params['action'] == 'to_wishlist':
      to_wishlist(params)
    elif 'iptv' in params['action']:
      iptv(params)
  else:
    # Main
    open_folder(addon.getLocalizedString(30101)) # Menu

    if m.logged:
      add_menu_option(addon.getLocalizedString(30104), get_url(action='tv'), icon='tv.png') # TV
      add_menu_option(addon.getLocalizedString(30107), get_url(action='epg'), icon='epg.png') # EGP
      add_menu_option(addon.getLocalizedString(30102), get_url(action='wishlist'), icon='mylist.png') # My list
      add_menu_option(addon.getLocalizedString(30103), get_url(action='recordings'), icon='recording.png') # Recordings
      add_menu_option(addon.getLocalizedString(30122), get_url(action='continue-watching'), icon='continue.png') # Continue
      add_menu_option(addon.getLocalizedString(30111), get_url(action='vod'), icon='vod.png') # VOD
      add_menu_option(addon.getLocalizedString(30112), get_url(action='search'), icon='search.png') # Search
      add_menu_option(addon.getLocalizedString(30180), get_url(action='profiles'), icon='profiles.png') # Profiles
      add_menu_option(addon.getLocalizedString(30108), get_url(action='devices'), icon='devices.png') # Devices
    elif m.expired_access_token:
      show_notification(addon.getLocalizedString(30208))

    add_menu_option(addon.getLocalizedString(30160), get_url(action='accounts'), icon='account.png') # Accounts
    add_menu_option(addon.getLocalizedString(30450), get_url(action='show_donation_dialog'), icon='qr.png') # Donation
    close_folder(cacheToDisc=False)


def run():
  # Call the router function and pass the plugin call parameters to it.
  # We use string slicing to trim the leading '?' from the plugin call paramstring
  params = sys.argv[2][1:]

  if 'show_donation_dialog' in params:
    from .customdialog import show_donation_dialog
    show_donation_dialog()
    return

  global m
  reuse_devices = addon.getSettingBool('reuse_devices')
  LOG('profile_dir: {}'.format(profile_dir))
  LOG('reuse_devices: {}'.format(reuse_devices))
  m = Movistar(profile_dir, reuse_devices=reuse_devices)
  m.add_extra_info = addon.getSettingBool('add_extra_info')
  if addon.getSettingBool('uhd'):
    m.quality = 'UHD'

  profile_id = addon.getSetting('profile_id').upper()
  LOG('profile_id: {}'.format(profile_id))
  if profile_id not in ['', 'AUTO']:
    m.account['platform'] = profile_id

  # Clear cache
  LOG('Cleaning cache. {} files removed.'.format(m.cache.clear_cache()))

  if '/iptv/channels' in sys.argv[0]: params += '&action=iptv-channels'
  elif '/iptv/epg' in sys.argv[0]: params += '&action=iptv-epg'
  router(params)
