# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import sys
import base64
import json
import requests
import io
import os
import time
import re

from .log import LOG, print_json
from .network import Network
from .cache import Cache
from .timeconv import *

class Movistar(object):
    account = {'username': '', 'password': '',
               'device_id': '',
               'id': None,
               'pid': None,
               'encoded_user': '',
               'profile_id': '0',
               'platform': '',
               'access_token': '',
               'session_token': '',
               'ssp_token': '',
               'demarcation': 0}

    def __init__(self, config_directory, reuse_devices=False):
      self.logged = False

      # Network
      headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Origin': 'https://ver.movistarplus.es',
        'Referer': 'https://ver.movistarplus.es/',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
      }
      self.net = Network()
      self.net.headers = headers

      # Cache
      self.cache = Cache(config_directory)

      # Access token
      self.load_key_file() # Default access_token
      content = self.cache.load_file('access_token.conf')
      if content:
        self.account['access_token'] = content
      #LOG('access_token: {}'.format(self.account['access_token']))
      if not self.account['access_token']: return

      # Endpoints
      self.endpoints = self.get_endpoints()

      # Account
      data = None
      content = self.cache.load('account.json')
      if content:
        data = json.loads(content)
      if not data or 'ofertas' not in data:
        data = self.authenticate()
        if not data or 'ofertas' not in data: return
        self.cache.save_file('account.json', json.dumps(data, ensure_ascii=False))
      self.account['id'] = data['ofertas'][0]['accountNumber']
      self.account['pid'] = data['ofertas'][0]['cod_persona']
      self.account['encoded_user'] = data['cod_usuario_cifrado']
      self.account['platform'] = data['ofertas'][0]['@id_perfil']

      # Profile ID
      content = self.cache.load_file('profile_id.conf')
      if content:
        self.account['profile_id'] = content

      # Device ID
      self.account['device_id'] = self.cache.load_file('device_id.conf')
      if not reuse_devices:
        LOG('not reusing devices')
        if not self.account['device_id']:
          self.account['device_id'] = self.new_device_id()
          self.cache.save_file('device_id.conf', self.account['device_id'])

        # Check if device is registered
        device_list = self.get_devices()
        found_device = False
        for device in device_list:
          if device['id'] == self.account['device_id']:
            found_device = True
            break
        if not found_device:
          LOG('device not found, trying to register device')
          self.register_device()
          device_list = self.get_devices(use_cache=False) # To store the updated list in cache
      else:
        LOG('reusing devices')
        # Check if device is registered
        device_list = self.get_devices()
        found_device = False
        wp_device = None
        for device in device_list:
          if not wp_device and device['type_code'] == 'WP':
            wp_device = device['id']
          if device['id'] == self.account['device_id']:
            found_device = True
            break
        if not found_device:
          if wp_device:
            LOG('device not found, using {}'.format(wp_device))
            self.account['device_id'] = wp_device
          else:
            LOG('device not found, registering new device')
            self.account['device_id'] = self.new_device_id()
            self.register_device()
            device_list = self.get_devices(use_cache=False) # To store the updated list in cache
          self.cache.save_file('device_id.conf', self.account['device_id'])
      LOG('device_id: {}'. format(self.account['device_id']))

      # Tokens
      content = self.cache.load('tokens.json', 3)
      if content:
        data = json.loads(content)
      else:
        LOG('Loading tokens')
        data = self.get_token()
        #print_json(data)
        if 'accessToken' in data:
          self.cache.save_file('tokens.json', json.dumps(data, ensure_ascii=False))
          self.cache.save_file('access_token.conf', data['accessToken'])

      self.account['session_token'] = ''
      self.account['ssp_token'] = ''

      self.entitlements = {}

      if 'accessToken' in data:
        self.account['access_token'] = data['accessToken']
        self.account['session_token'] = data['token']
        self.account['ssp_token'] = data['sspToken']
        self.account['demarcation'] = data['demarcation']

        self.entitlements['activePurchases'] = data['activePurchases']
        self.entitlements['partners'] = data['partners']
        self.entitlements['activePackages'] = data['activePackages']
        self.entitlements['vodSubscription'] = data['vodSubscription'].split(',')
        self.entitlements['linearSubscription'] = data['linearSubscription'].split(',')
        self.entitlements['suscripcion'] = data['suscripcion']
        #print_json(self.entitlements)
        self.logged = True

    def install_key_file(self, filename):
      import shutil
      if sys.version_info[0] > 2:
        filename = bytes(filename, 'utf-8')
      shutil.copyfile(filename, self.cache.config_directory + 'auth.key')

    def load_key_file(self):
      content = self.cache.load_file('auth.key')
      if content:
        data = json.loads(content)
        data = json.loads(data['data'])
        self.account['access_token'] = data['response']['access_token']

    def get_token(self):
      data = {"accountNumber": self.account['id'],
              "userProfile": self.account['profile_id'],
              "streamMiscellanea":"HTTPS",
              "deviceType":"WP_OTT",
              "deviceManufacturerProduct":"Firefox",
              "streamDRM":"Widevine",
              "streamFormat":"DASH",
      }

      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Movistarplus-Ui'] = '2.36.30'
      headers['X-Movistarplus-Os'] = 'Linux88'
      headers['X-Movistarplus-Deviceid'] = self.account['device_id']
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      #print_json(data)
      #print_json(headers)

      url = self.endpoints['initdata'].format(deviceType='webplayer', DEVICEID=self.account['device_id'])
      response = self.net.session.post(url, data=json.dumps(data), headers=headers)
      content = response.content.decode('utf-8')
      #LOG('get_token response: {}'.format(content))
      try:
        d = json.loads(content)
      except:
        d = {'error': content}
      return d

    def clear_session(self):
      headers = self.net.headers.copy()
      headers['Access-Control-Request-Method'] = 'POST'
      headers['Access-Control-Request-Headers'] = 'content-type,x-hzid'
      url = self.endpoints['setUpStream'].format(PID=self.account['pid'], deviceCode='WP_OTT', PLAYREADYID=self.account['device_id'])
      response = self.net.session.options(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def open_session(self, data, session_token, session_id = None):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = session_token
      url = self.endpoints['setUpStream'].format(PID=self.account['id'], deviceCode='WP_OTT', PLAYREADYID=self.account['device_id'])
      if session_id != None:
         url += '/' + session_id
      #LOG('open_session: url: {}'.format(url))
      #LOG('open_session: data: {}'.format(data))
      response = self.net.session.post(url, data=data, headers=headers)
      content = response.content.decode('utf-8')
      try:
        d = json.loads(content)
      except:
        d = None
      #LOG("**** open_session response: {}".format(d))
      return d

    def login(self):
      headers = self.net.headers.copy()
      headers['x-movistarplus-deviceid'] = self.account['device_id']
      headers['x-movistarplus-ui'] = '2.36.30'
      headers['x-movistarplus-os'] = 'Linux88'

      if sys.version_info[0] < 3:
        p = base64.b64decode(bytes(self.account['password']))
      else:
        p = base64.b64decode(bytes(self.account['password'], encoding='ascii')).decode('ascii')

      data = {
          'grant_type': 'password',
          'deviceClass': 'webplayer',
          'username': self.account['username'],
          'password': p,
          'captchaResult': '',
      }

      url = self.endpoints['token']
      response = self.net.session.post(url, headers=headers, data=data)
      print(response.content)

    def authenticate(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
      #headers['x-movistarplus-deviceid'] = self.account['device_id']
      headers['x-movistarplus-ui'] = '2.36.30'
      headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['autenticacion_tk'] + '?_=' + str(int(time.time()*1000))
      #LOG('authenticate: headers: {}'.format(headers))
      data = self.net.load_data(url, headers)
      #LOG('authenticate: data: {}'.format(data))
      return data

    def load_service_directory(self):
      url = 'https://homeservicedirectory.dof6.com/VoD/vod.svc/webplayer/environments/prod/ws-directory?format=json'
      return self.net.load_data(url)

    def get_endpoints(self):
      endpoints = {}
      content = self.cache.load('endpoints.json')
      if content:
        data = json.loads(content)
      else:
        data = self.load_service_directory()
        self.cache.save_file('endpoints.json', json.dumps(data, ensure_ascii=False))

      for services in data['services']['service']:
        if isinstance(services['endpoint'], list):
          for endpoint in services['endpoint']:
            endpoints[endpoint['@name']] = endpoint['@address']
        else:
          endpoint = services['endpoint']
          endpoints[endpoint['@name']] = endpoint['@address']
      return endpoints

    def change_device(self, id):
      self.account['device_id'] = id
      self.cache.save_file('device_id.conf', self.account['device_id'])
      self.cache.remove_file('tokens.json')

    def get_devices(self, use_cache=True):
      content = self.cache.load('devices.json', 3)
      if use_cache and content:
        data = json.loads(content)
      else:
        headers = self.net.headers.copy()
        headers['Authorization'] = 'Bearer ' + self.account['access_token']
        url = self.endpoints['obtenerdipositivos'].format(ACCOUNTNUMBER=self.account['id'])
        data = self.net.load_data(url, headers)
        self.cache.save_file('devices.json', json.dumps(data, ensure_ascii=False))
      #print_json(data)
      res = []
      for d in data:
        if d['Id'] != '-':
          dev = {}
          dev['id'] = d['Id']
          dev['name'] = d['Name']
          dev['type'] = d['DeviceType']
          dev['type_code'] = d['DeviceTypeCode']
          dev['playing'] = d['ContentPlaying']
          dev['reg_date'] = isodate2str(d['RegistrationDate'])
          dev['in_ssp'] = d['IsInSsp']
          res.append(dev)
      return res

    def register_device(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['x-movistarplus-deviceid'] = self.account['device_id']
      headers['x-movistarplus-ui'] = '2.36.30'
      headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['activacion_dispositivo_cuenta_tk'].format(ACCOUNTNUMBER=self.account['id'], DEVICEID=self.account['device_id'])
      response = self.net.session.post(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def unregister_device(self):
      return self.delete_device(self.account['device_id'])

    def new_device_id(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['x-movistarplus-ui'] = '2.36.30'
      headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = 'https://auth.dof6.com/movistarplus/webplayer/accounts/'+ self.account['id'] + '/devices/?qspVersion=ssp'
      response = self.net.session.post(url, headers=headers)
      content = response.content.decode('utf-8')
      return content.replace('"', '')

    def delete_device(self, device_id):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['Authorization'] = 'bearer ' + self.account['access_token']
      url = self.endpoints['eliminardipositivo'].format(ACCOUNTNUMBER=self.account['id'], DEVICEID=device_id)
      response = self.net.session.delete(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def rename_device(self, device_id, name):
      headers = self.net.headers.copy()
      headers['Authorization'] = 'bearer ' + self.account['access_token']
      url = self.endpoints['nombrardispositivo'].format(ACCOUNTNUMBER=self.account['id'], DEVICEID=device_id)
      response = self.net.session.put(url, headers=headers, json=name)
      content = response.content.decode('utf-8')
      return content

    def delete_session_id(self, session_token, id = '0'):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'text/plain;charset=UTF-8'
      data = '{"X-HZId":"' + session_token +'","X-Content-Type":"application/json","X-Operation":"DELETE"}'
      url = self.endpoints['tearDownStream'].format(PID=self.account['pid'], deviceCode='WP_OTT', PLAYREADYID=self.account['device_id'], SessionID=id)
      response = self.net.session.post(url, headers=headers, data=data)
      content = response.content.decode('utf-8')
      return content

    """
    def delete_last_session(self):
      token = self.cache.load_file('session_token.conf')
      if token:
        self.delete_session0(token)
        os.remove(self.cache.config_directory + 'session_token.conf')
    """

    def delete_session(self, device_id = None):
      if device_id == None: device_id = self.account['device_id']
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['Authorization'] = 'bearer ' + self.account['access_token']
      url = self.endpoints['cerrarsesiondispositivo'].format(ACCOUNTNUMBER=self.account['id'], DEVICEID=device_id)
      response = self.net.session.delete(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def get_profiles(self):
      headers = self.net.headers.copy()
      headers['X-HZId'] = self.account['session_token']
      url = self.endpoints['listaperfiles']
      data = self.net.load_data(url, headers=headers)
      res = []
      for d in data['items']:
        p = {}
        p['id'] = d['id']
        p['name'] = d['name']
        p['for_kids'] = d['isForKids']
        p['type'] = d['typeID']
        p['image_id'] = d['imageID']
        res.append(p)
      return res

    def change_profile(self, id):
      self.account['profile_id'] = id
      self.cache.save_file('profile_id.conf', self.account['profile_id'])
      self.cache.remove_file('tokens.json')

    def get_epg(self):
      content = self.cache.load('epg2.json', 6*60)
      if content:
        data = json.loads(content)
      else:
        today = datetime.today()
        str_now = today.strftime('%Y-%m-%dT%H:00:00')
        url = self.endpoints['rejilla'].format(deviceType='webplayer', profile=self.account['platform'], UTCDATETIME=str_now, DURATION=2, CHANNELS='', NETWORK='movistarplus', mdrm='true', demarcation=self.account['demarcation'])
        data = self.net.load_data(url)
        self.cache.save_file('epg2.json', json.dumps(data, ensure_ascii=False))

      epg = {}
      for ch in data:
        id = ch[0]['Canal']['CodCadenaTv']
        if not id in epg: epg[id] = []
        for p in ch:
          pr = {}
          pr['start'] = int(p['FechaHoraInicio'])
          pr['end'] = int(p['FechaHoraFin'])
          pr['start_str'] = timestamp2str(pr['start'])
          pr['end_str'] = timestamp2str(pr['end'])
          pr['desc1'] = p['Titulo']
          pr['desc2'] = ''
          if 'TituloHorLinea2' in p:
            pr['desc2'] = p['TituloHorLinea2']
          epg[id].append(pr)

      return epg

    def find_program_epg(self, epg, id, timestamp):
      found = False
      c = 0
      programs = []
      for p in epg[id]:
        #print(p)
        if (p['start'] <= timestamp) and (timestamp <= p['end']):
          found = True
        if found:
          programs.append(p)
          c += 1
          if (c > 5): break;
      return programs

    def colorize_title(self, title):
      s = title['info']['title']

      stype = title.get('stream_type')
      if stype == 'u7d': s += ' (U7D)'
      elif stype == 'rec': s += ' (REC)'

      if title['subscribed'] == True:
        color1 = 'yellow'
        color2 = 'red'
      else:
        color1 = 'gray'
        color2 = 'gray'
        s = '[COLOR gray]' + s +'[/COLOR]'
      if title.get('desc1', '') != '':
        s += ' - [COLOR {}]{}[/COLOR]'.format(color1, title['desc1'])
      if title.get('desc2', '') != '':
        s += ' - [COLOR {}]{}[/COLOR]'.format(color2, title['desc2'])
      return s

    def add_epg_info(self, channels, epg, timestamp):
      for ch in channels:
        programs = self.find_program_epg(epg, ch['id'], timestamp)
        ch['info']['plot'] = ''
        for i in range(len(programs)):
          desc1 = programs[i]['desc1']
          desc2 = programs[i]['desc2']
          if i == 0:
            ch['desc1'] = desc1
            ch['desc2'] = desc2
          ch['info']['plot'] += "[B]{}[/B] {} {}\n".format(programs[i]['start_str'], desc1, desc2)

    def is_subscribed_channel(self, products):
      for e in self.entitlements['activePackages']:
        if e['name'] in products:
           return True
      for e in self.entitlements['activePurchases']:
        if e['name'] in products:
           return True
      return False

    def is_subscribed_vod(self, products):
      for p in products:
        if p['Nombre'] in self.entitlements['vodSubscription']:
           return True
      return False

    def get_channels(self, add_epg_info = False):
      if add_epg_info:
        url = self.endpoints['guiaTV'].format(deviceType='webplayer', profile=self.account['platform'], preOffset=0, postOffset=0, mdrm='true', demarcation=self.account['demarcation'])
        data = self.net.load_data(url)
      else:
        content = self.cache.load('channels2.json')
        if content:
          data = json.loads(content)
        else:
          url = self.endpoints['canales'].format(deviceType='webplayer', profile=self.account['platform'], mdrm='true', demarcation=self.account['demarcation'])
          data = self.net.load_data(url)
          self.cache.save_file('channels2.json', json.dumps(data, ensure_ascii=False))

      res = []
      for c in data:
        t = {}
        t['info'] = {}
        t['art'] = {}
        t['type'] = 'movie'
        t['stream_type'] = 'tv'
        t['info']['mediatype'] = 'movie'
        t['info']['title'] = str(c['Dial']) +'. ' + c['Nombre']
        t['id'] = c['CodCadenaTv']
        if add_epg_info:
          t['desc1'] = c['Nombre']
          t['desc2'] = ''
        t['dial'] = c['Dial']
        t['url'] = c['PuntoReproduccion']
        t['art']['icon'] = c['Logo']
        t['art']['thumb'] = c['Logo']
        t['art']['poster'] = c['Logo']
        t['session_request'] = '{"contentID":"'+ t['id'] +'", "streamType":"CHN"}'
        t['subscribed'] = self.is_subscribed_channel(c['Productos'])
        t['info']['playcount'] = 1 # Set as watched
        # epg
        if add_epg_info:
          program = c['Pases'][0]
          t['desc1'] = program['Titulo']
          if 'TituloHorLinea2' in program:
            t['desc2'] = program['TituloHorLinea2']
          t['start'] = int(program['FechaHoraInicio'])
          t['end'] = int(program['FechaHoraFin'])
          t['start_str'] = timestamp2str(t['start'])
          t['end_str'] = timestamp2str(t['end'])
          t['info']['plot'] = '[B]{}-{}[/B] {}\n{}'.format(t['start_str'], t['end_str'], t['desc1'], t['desc2'])

        res.append(t)

      return res

    def get_channels_with_epg(self):
      channels = self.get_channels()
      epg = self.get_epg()
      import time
      now = int(time.time() * 1000)
      self.add_epg_info(channels, epg, now)
      return channels

    def download_list(self, url, use_hz = False):
      headers = self.net.headers.copy()
      headers['Accept'] = 'application/vnd.miviewtv.v1+json'
      headers['Content-Type'] = 'application/json'
      if use_hz:
        headers['Authorization'] = 'Bearer ' + self.account['access_token']
        headers['X-Hzid'] = self.account['session_token']

      return self.net.load_data(url, headers)

    def get_wishlist_url(self):
      url = self.endpoints['favoritos'].format(
              deviceType='webplayer', DIGITALPLUSUSERIDC=self.account['encoded_user'], PROFILE=self.account['platform'],
              ACCOUNTNUMBER=self.account['id'], idsOnly='false', start=1, end=30, mdrm='true', demarcation=self.account['demarcation'])
      #url += '&filter=AD-SINX&topic=CN'
      url += '&_='+ str(int(time.time()*1000))
      return url

    def get_recordings_url(self):
      url = self.endpoints['grabaciones'].format(
              deviceType='webplayer', DIGITALPLUSUSERIDC=self.account['encoded_user'], PROFILE=self.account['platform'],
              idsOnly='false', start=1, end=30, mdrm='true', demarcation=self.account['demarcation'])
      url += '&state=Completed&_='+ str(int(time.time()*1000))
      return url

    def get_title(self, data):
      t = {}
      t['info'] = {}
      t['art'] = {}
      ed = data['DatosEditoriales']
      t['id'] = ed['Id']
      t['info']['title'] = ed['Titulo']
      t['art']['poster'] = ed['Imagen'].replace('ywcatalogov', 'dispficha')
      t['art']['thumb'] = t['art']['poster']
      t['info']['genre'] = ed['GeneroComAntena']
      if ed['TipoContenido'] in ['Individual', 'Episodio']:
        t['type'] = 'movie'
        t['stream_type'] = 'vod'
        t['info']['mediatype'] = 'movie'
        t['info']['duration'] = ed['DuracionEnSegundos']
        t['url'] = ''
        t['session_request'] = ''
        if len(data['VodItems']) > 0:
          video = data['VodItems'][0]
          t['subscribed'] = self.is_subscribed_vod(video['Productos'])
          if not 'UrlVideo' in video: return None
          t['url'] = video['UrlVideo']
          if video['AssetType'] == 'VOD':
            t['session_request'] = '{"contentID":' + str(t['id']) + ',"drmMediaID":"' + video['CasId'] +'", "streamType":"AST"}'
          elif video['AssetType'] == 'U7D':
            t['stream_type'] = 'u7d'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"CUTV"}'
          elif video['AssetType'] == 'NPVR':
            t['stream_type'] = 'rec'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"NPVR"}'
      if ed['TipoContenido'] == 'Serie':
        t['type'] = 'series'
        t['info']['mediatype'] = 'tvshow'
        t['subscribed'] = self.is_subscribed_vod(data['Productos'])
      if ed['TipoContenido'] == 'Temporada':
        t['type'] = 'season'
        t['info']['mediatype'] = 'season'
        t['subscribed'] = self.is_subscribed_vod(data['Productos'])

      return t

    def get_list(self, data):
      res = []
      for d in data:
        #print_json(d)
        t = self.get_title(d)
        if t and t['id'] != '':
          res.append(t)
      return res

    def get_seasons(self, id):
      url = self.endpoints['ficha'].format(deviceType='webplayer', id=id, profile=self.account['platform'], mediatype='FOTOV', version='7.1', mode='GLOBAL', catalog='', channels='', state='', mdrm='true', demarcation=self.account['demarcation'], legacyBoxOffice='')
      data = self.net.load_data(url)
      #print_json(data)
      res = []
      c = 1
      for d in data['Temporadas']:
        t = {}
        t['id'] = d['Id']
        t['info'] = {}
        t['art'] = {}
        t['type'] = 'season'
        t['info']['mediatype'] = 'season'
        t['info']['title'] = d['Titulo']
        t['info']['tvshowtitle'] = data['TituloSerie']
        t['info']['plot'] = data['Descripcion']
        t['info']['season'] = c
        t['art']['poster'] = t['art']['thumb'] = data['Imagen']
        t['subscribed'] = self.is_subscribed_vod(data['Productos'])
        c += 1
        res.append(t)

      return res

    def get_episodes(self, id):
      url = self.endpoints['ficha'].format(deviceType='webplayer', id=str(id), profile=self.account['platform'], mediatype='FOTOV', version='7.1', mode='GLOBAL', catalog='', channels='', state='', mdrm='true', demarcation=self.account['demarcation'], legacyBoxOffice='')
      #print(url)
      data = self.net.load_data(url)
      #print_json(data)
      res = []
      for d in data['Episodios']:
        ed = d['DatosEditoriales']
        t = {}
        t['id'] = ed['Id']
        t['info'] = {}
        t['art'] = {}
        t['type'] = 'movie'
        t['info']['mediatype'] = 'episode'
        t['stream_type'] = 'vod'
        t['info']['title'] = ed['TituloEpisodio']
        t['info']['episode'] = ed['NumeroEpisodio']
        t['info']['duration'] = ed['DuracionEnSegundos']
        t['art']['thumb'] = ed['Imagen']
        for im in ed['Imagenes']:
          if im['id'] == 'horizontal': t['art']['thumb'] = im['uri']
        m = re.search(r'T(\d+)', ed['Temporada'])
        if m: t['info']['season'] = m.group(1)
        t['url'] = ''
        t['session_request'] = ''
        if len(d['VodItems']) > 0:
          video = d['VodItems'][0]
          t['subscribed'] = self.is_subscribed_vod(video['Productos'])
          t['url'] = video['UrlVideo']
          if video['AssetType'] == 'VOD':
            t['session_request'] = '{"contentID":' + str(t['id']) + ',"drmMediaID":"' + video['CasId'] +'", "streamType":"AST"}'
          elif video['AssetType'] == 'U7D':
            t['stream_type'] = 'u7d'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"CUTV"}'

        res.append(t)

      return res

    def get_u7d_url(self, url):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-HZId'] = self.account['session_token']
      data = self.net.load_data(url, headers)
      return data

    def get_subtitles(self, manifest_url):
      base_url = os.path.dirname(manifest_url)
      content = self.net.load_url(manifest_url)
      rx = r'<AdaptationSet id="\d+" contentType="text" mimeType="application\/ttml\+xml" lang="(.*?)">.*?<BaseURL>(.*?)<\/BaseURL>'
      matches = re.findall(rx, content, flags=re.MULTILINE | re.DOTALL)
      res = []
      for m in matches:
        sub = {}
        sub['lang'] = m[0]
        sub['filename'] = m[1]
        sub['url'] = base_url +'/' + sub['filename']
        if sub['lang'] == 'srd': sub['lang'] = 'es [CC]'
        if sub['lang'] == 'qaa': sub['lang'] = 'en [VO]'
        res.append(sub)
      return res

    def download_subtitles(self, sublist):
      output_dir = self.cache.config_directory + 'subtitles'
      #LOG('output_dir: {}'.format(output_dir))
      if not os.path.exists(output_dir):
        os.makedirs(output_dir)
      res = []
      for s in sublist:
        filename = output_dir + os.sep + s['lang'] + '.ttml'
        LOG('filename: {}'.format(filename))
        content = self.net.load_url(s['url'])
        with io.open(filename, 'w', encoding='utf-8', newline='') as handle:
          handle.write(content)
        res.append(filename)
      return res

    def get_vod_list_url(self, cat='movies'):
      #sort = 'FD'
      sort = 'MA'
      url = self.endpoints['consultar'].format(deviceType='webplayer', profile=self.account['platform'], sort=sort, start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
      filter = '&filter=AC-OM,AC-MA,MA-GBLCICLO59,TD-CUP,RG-SINCAT,AC-PREPUB,' + self.entitlements['suscripcion']
      url += '&mode=VOD' + filter
      if cat == 'tvshows':
        url += '&topic=SR&showSeries=series'
      elif cat == 'movies':
        url += '&topic=CN'
      elif cat == 'documentaries':
        url += '&topic=DC'
      elif cat == 'kids':
        url += '&topic=IN'
      #LOG('vod url: {}'.format(url))
      return url
