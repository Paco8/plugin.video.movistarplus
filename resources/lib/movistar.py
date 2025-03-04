# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import sys
import json
import requests
import io
import os
import time
import re
import shutil
import glob

from datetime import datetime, timedelta

from .endpoints import endpoints
from .log import LOG, print_json
from .network import Network
from .cache import Cache
from .timeconv import *
from .useragent import useragent

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

    add_extra_info = True
    #dplayer = 'webplayer'
    #device_code = 'WP_OTT'
    #manufacturer = 'Firefox'
    dplayer = 'amazon.tv'
    device_code = 'SMARTTV_OTT'
    manufacturer = 'LG'
    account_dir = 'account_1'

    def __init__(self, config_directory, reuse_devices=False):
      self.logged = False
      self.expired_access_token = False

      # Network
      headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Origin': 'https://ver.movistarplus.es',
        'Referer': 'https://ver.movistarplus.es/',
        'User-Agent': useragent
      }
      self.net = Network()
      self.net.headers = headers

      self.quality = 'HD' # or UHD

      # Account dir
      content = Movistar.load_file_if_exists(config_directory + 'account.txt')
      if content: self.account_dir = content
      LOG('account_dir: {}'.format(self.account_dir))

      account_dir = os.path.join(config_directory, self.account_dir)
      if not os.path.exists(account_dir):
        os.makedirs(account_dir)
        # Migrate data
        if self.account_dir == 'account_1':
          for ext in ['*.conf', '*.json', '*.key']:
            for f in glob.glob(os.path.join(config_directory, ext)):
              #LOG(f)
              shutil.move(f, account_dir)
          if os.path.exists(config_directory + 'cache'):
            #LOG(config_directory + 'cache')
            shutil.move(config_directory + 'cache', account_dir)

      self.config_dir = config_directory
      config_directory = account_dir + '/'

      # Cache
      self.cache = Cache(config_directory)
      if not os.path.exists(config_directory + 'cache'):
        os.makedirs(config_directory + 'cache')

      # Endpoints
      self.endpoints = endpoints

      # Access token
      self.load_key_file() # Default access_token
      if self.account['access_token']:
        exp = self.get_token_expire_date(self.account['access_token'])
        #LOG('auth.key: expiring date: {}'.format(exp))
        if exp < time.time():
          self.expired_access_token = True
          self.account['access_token'] = None

      content = self.cache.load_file('access_token.conf')
      if content:
        exp = self.get_token_expire_date(content)
        #LOG('access_token.conf: expiring date: {}'.format(exp))
        if exp < time.time():
          self.expired_access_token = True
        else:
          self.account['access_token'] = content
      #LOG('access_token: {}'.format(self.account['access_token']))
      LOG('expired_access_token: {}'.format(self.expired_access_token))

      if not self.account['access_token']: return

      # Account
      data = None
      content = self.cache.load('account.json')
      if content:
        data = json.loads(content)
      if not data or 'ofertas' not in data:
        data = self.get_account_info()
        if not data or 'ofertas' not in data: return
        self.cache.save_file('account.json', json.dumps(data, ensure_ascii=False))
      self.account['id'] = data['ofertas'][0]['accountNumber']
      #self.account['pid'] = data['ofertas'][0]['cod_persona']
      self.account['encoded_user'] = data['cod_usuario_cifrado']
      self.account['platform'] = data['ofertas'][0]['@id_perfil']
      #self.account['platform'] = 'OTT'

      # Profile ID
      content = self.cache.load_file('profile_id.conf')
      if content:
        self.account['profile_id'] = content

      # Device ID
      self.account['device_id'] = self.cache.load_file('device_id.conf')
      if self.account['device_id']:
        self.account['device_id'] = self.account['device_id'].strip('"')
      else:
        # Create new device
        if not reuse_devices:
          LOG('not reusing devices')
          if not self.account['device_id']:
            self.account['device_id'] = self.request_device_id()
            self.cache.save_file('device_id.conf', self.account['device_id'])
        else:
          LOG('reusing devices')
          # Check if device is registered
          device_list = self.get_devices()
          found_device = False
          wp_device = None
          for device in device_list:
            if not wp_device: # and device['type_code'] == 'WP':
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
              self.account['device_id'] = self.request_device_id()
            self.cache.save_file('device_id.conf', self.account['device_id'])
      LOG('device_id: {}'. format(self.account['device_id']))

      # Tokens
      content = self.cache.load('tokens.json', 5)
      if content:
        data = json.loads(content)
      else:
        LOG('Loading tokens')
        data = self.get_token()
        if 'error' in data and self.account['device_id']:
          # Try registering the device
          self.register_device()
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
        self.account['pid'] = data['pid']

        self.entitlements['activePurchases'] = data['activePurchases']
        self.entitlements['partners'] = data['partners']
        self.entitlements['activePackages'] = data['activePackages']
        self.entitlements['vodSubscription'] = data['vodSubscription'].split(',') if data['linearSubscription'] else []
        self.entitlements['linearSubscription'] = data['linearSubscription'].split(',') if data['linearSubscription'] else []
        self.entitlements['suscripcion'] = data['suscripcion']
        self.entitlements['tvRights'] = data['tvRights']
        self.entitlements['distilledTvRights'] = data['distilledTvRights']
        #print_json(self.entitlements)
        self.logged = True

      # Search
      data = self.cache.load_file('searchs.json')
      self.search_list = json.loads(data) if data else []

    def get_token(self):
      data = {"accountNumber": self.account['id'],
              "userProfile": self.account['profile_id'],
              "streamMiscellanea":"HTTPS",
              "deviceType": self.device_code,
              "deviceManufacturerProduct": self.manufacturer,
              "streamDRM":"Widevine",
              "streamFormat":"DASH",
      }

      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      #headers['X-Movistarplus-Ui'] = '2.36.30'
      #headers['X-Movistarplus-Os'] = 'Linux88'
      headers['X-Movistarplus-Deviceid'] = self.account['device_id']
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      #print_json(data)
      #print_json(headers)

      url = self.endpoints['initdata'].format(deviceType=self.dplayer, DEVICEID=self.account['device_id'])
      response = self.net.session.post(url, data=json.dumps(data), headers=headers)
      content = response.content.decode('utf-8')
      LOG('get_token response: {}'.format(content))
      try:
        d = json.loads(content)
      except:
        d = {'error': content}
      return d

    def clear_session(self):
      headers = self.net.headers.copy()
      headers['Access-Control-Request-Method'] = 'POST'
      headers['Access-Control-Request-Headers'] = 'content-type,x-hzid'
      url = self.endpoints['setUpStream'].format(PID=self.account['pid'], deviceCode=self.device_code, PLAYREADYID=self.account['device_id'])
      response = self.net.session.options(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def open_session(self, data, session_token=None, session_id=None):
      if not session_token:
        session_token = self.account['session_token']
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = session_token
      url = self.endpoints['setUpStream'].format(PID=self.account['pid'], deviceCode=self.device_code, PLAYREADYID=self.account['device_id'])
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
      #LOG("open_session: response: {}".format(d))
      return d

    def login(self, username, password):
      headers = self.net.headers.copy()
      if self.account['device_id']:
        headers['x-movistarplus-deviceid'] = self.account['device_id']
      #headers['x-movistarplus-ui'] = '2.36.30'
      #headers['x-movistarplus-os'] = 'Linux88'
      #LOG(headers)

      data = {
          'grant_type': 'password',
          'deviceClass': self.dplayer,
          'username': username,
          'password': password,
      }
      #LOG(data)

      url = self.endpoints['token'].format(deviceType=self.dplayer)
      #LOG(url)

      response = self.net.session.post(url, headers=headers, data=data)
      content = response.content.decode('utf-8')
      LOG(content)
      success = False
      try:
        d = json.loads(content)
        if 'access_token' in d:
          success = True
          self.save_key_file(d)
      except:
        pass
      return success, content

    def get_account_info(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
      #headers['x-movistarplus-deviceid'] = self.account['device_id']
      #headers['x-movistarplus-ui'] = '2.36.30'
      #headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['autenticacion_tk'].format(deviceType=self.dplayer) + '?_=' + str(int(time.time()*1000))
      #LOG(url)
      #LOG('get_account_info: headers: {}'.format(headers))
      data = self.net.load_data(url, headers)
      #LOG('get_account_info: data: {}'.format(data))
      return data

    def change_device(self, id):
      self.account['device_id'] = id
      self.cache.save_file('device_id.conf', self.account['device_id'])
      self.cache.remove_file('tokens.json')

    def get_devices(self):
      headers = self.net.headers.copy()
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['obtenerdipositivos'].format(ACCOUNTNUMBER=self.account['id'])
      data = self.net.load_data(url, headers)
      #print_json(data)
      if not isinstance(data, list): return []
      res = []
      for d in data:
        if d.get('Id') != '-':
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
      #headers['x-movistarplus-ui'] = '2.36.30'
      #headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['activacion_dispositivo_cuenta_tk'].format(deviceType=self.dplayer, ACCOUNTNUMBER=self.account['id'], DEVICEID=self.account['device_id'])
      response = self.net.session.post(url, headers=headers)
      content = response.content.decode('utf-8')
      return content

    def unregister_device(self):
      return self.delete_device(self.account['device_id'])

    def request_device_id(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      #headers['x-movistarplus-ui'] = '2.36.30'
      #headers['x-movistarplus-os'] = 'Linux88'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = 'https://auth.dof6.com/movistarplus/{deviceType}/accounts/{ACCOUNTNUMBER}/devices/?qspVersion=ssp'
      url = url.format(deviceType=self.dplayer, ACCOUNTNUMBER=self.account['id'])
      #LOG(url)
      response = self.net.session.post(url, headers=headers)
      content = response.content.decode('utf-8')
      return content.strip('"')

    #def generate_device_id(self):
    #  import random
    #  s = ''
    #  for _ in range(0, 32): s += random.choice('abcdef0123456789')
    #  return s

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
      url = self.endpoints['tearDownStream'].format(PID=self.account['pid'], deviceCode=self.device_code, PLAYREADYID=self.account['device_id'], SessionID=id)
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

    def get_cdntoken(self):
      headers = self.net.headers.copy()
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['renovacion_cdntoken2'].format(deviceType=self.dplayer, ACCOUNTNUMBER=self.account['id'])
      data = self.net.post_data(url, None, headers)
      if isinstance(data, dict):
        return data.get('access_token')
      return ''

    def get_session_token(self):
      data = {"accountNumber": self.account['id'],
              "sessionUserProfile": self.account['profile_id'],
              "streamMiscellanea":"HTTPS",
              "deviceType": self.device_code,
              "deviceManufacturerProduct": self.manufacturer,
              "streamDRM":"Widevine",
              "streamFormat":"DASH",
      }
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['renovacion_hztoken'].format(deviceType=self.dplayer, DEVICEID=self.account['device_id'])
      data = self.net.post_data(url, json.dumps(data), headers)
      return data.get('homeZoneID')

    def get_ssp_token(self):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['Authorization'] = 'Bearer ' + self.account['access_token']
      url = self.endpoints['renovacion_ssptoken'].format(deviceType=self.dplayer, ACCOUNTNUMBER=self.account['id'], DEVICEID=self.account['device_id'])
      data = self.net.post_data(url, '', headers)
      return data.get('access_token')

    def update_session_token(self):
      new_hz_token = self.get_session_token()
      if new_hz_token:
        self.account['session_token'] = new_hz_token
      return

    def get_profiles(self):
      headers = self.net.headers.copy()
      headers['X-HZId'] = self.account['session_token']
      url = self.endpoints['listaperfiles']
      data = self.net.load_data(url, headers=headers)
      res = []
      for d in data.get('items', []):
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

    def load_epg_data(self, date_str, duration=2, channels=''):
      demarcation = self.account['demarcation']
      url = self.endpoints['rejilla'].format(deviceType='webplayer', profile=self.account['platform'], UTCDATETIME=date_str, DURATION=duration, CHANNELS=channels, NETWORK='movistarplus', mdrm='true', demarcation=demarcation)
      if self.quality == 'UHD': url += '&filterQuality=UHD'
      #LOG(url)
      data = self.net.load_data(url)
      return data

    def get_epg(self, date=None, duration=2, channels=None):
      if channels or date:
        if not date:
          today = datetime.today()
          date = today.strftime('%Y-%m-%dT00:00:00')
        epg_data = self.load_epg_data(date, duration, channels if channels else '')
        if not epg_data or 'error' in epg_data: return {}
        if channels:
          data = []
          data.append(epg_data)
        else:
          data = epg_data
      else:
        cache_filename = 'epg_{}_{}.json'.format(self.quality, duration)
        content = self.cache.load(cache_filename, 6*60)
        if content:
          data = json.loads(content)
        else:
          today = datetime.today()
          str_now = today.strftime('%Y-%m-%dT00:00:00')
          data = self.load_epg_data(str_now, duration=duration)
          if not 'error' in data:
            self.cache.save_file(cache_filename, json.dumps(data, ensure_ascii=False))

      epg = {}
      if 'error' in data: return epg

      for ch in data:
        id = ch[0]['Canal']['CodCadenaTv']
        if not id in epg: epg[id] = []
        for p in ch:
          pr = {}
          pr['start'] = int(p['FechaHoraInicio'])
          pr['end'] = int(p['FechaHoraFin'])
          pr['start_str'] = timestamp2str(pr['start'])
          pr['end_str'] = timestamp2str(pr['end'])
          pr['date_str'] = timestamp2str(pr['start'], '%a %d %H:%M')
          pr['desc1'] = p['Titulo']
          pr['desc2'] = ''
          if 'TituloHorLinea2' in p:
            pr['desc2'] = p['TituloHorLinea2']
          pr['show_id'] = p['ShowId']
          if 'SerialId' in p:
            pr['serie_id'] = p['SerialId']
          pr['id'] = p['Id']
          #if 'links' in p: pr['links'] = p['links']
          epg[id].append(pr)

      return epg

    def find_program_epg(self, epg, id, timestamp):
      found = False
      c = 0
      programs = []
      if not id in epg: return programs
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
      if title.get('video_format') == '4K': s += " (4K)"

      color1 = 'yellow'
      color2 = 'red'

      available = True
      if 'subscribed' in title and title['subscribed'] == False: available = False
      if 'url' in title and title['url'] == '': available = False

      if not available:
        color1 = 'gray'
        color2 = 'gray'
        s = '[COLOR gray]' + s +'[/COLOR]'
      elif 'start' in title:
        aired = (title['start'] <= (time.time() * 1000))
        if not aired:
          color1 = 'blue'
          color2 = 'blue'
          s = '[COLOR blue]' + s +'[/COLOR]'
      if title.get('desc1', '') != '':
        s += ' - [COLOR {}]{}[/COLOR]'.format(color1, title['desc1'])
      if title.get('desc2', '') != '':
        s += ' - [COLOR {}]{}[/COLOR]'.format(color2, title['desc2'])
      return s

    def add_epg_info(self, channels, epg, timestamp):
      for ch in channels:
        programs = self.find_program_epg(epg, ch['id'], timestamp)
        plot = ''
        for i in range(len(programs)):
          desc1 = programs[i]['desc1']
          desc2 = programs[i]['desc2']
          if i == 0:
            ch['desc1'] = desc1
            ch['desc2'] = desc2
          plot += "[B]{}[/B] {} {}\n".format(programs[i]['start_str'], desc1, desc2)
          if self.add_extra_info:
            ch['art']['poster'] = ch['art']['fanart'] = None
            ch['show_id'] = programs[i]['show_id']
            self.add_video_extra_info(ch)
            if 'plot' in ch['info']:
              plot = plot + ch['info']['plot']
            break
        ch['info']['plot'] = plot

    def is_subscribed_channel(self, products):
      for e in self.entitlements['activePackages']:
        if e['name'] in products:
           return True
      for e in self.entitlements['activePurchases']:
        if e['name'] in products:
           return True
      for e in self.entitlements['tvRights']:
        if e in products:
           return True
      return False

    def is_subscribed_vod(self, products):
      #for p in products:
      #  if p['Nombre'] in self.entitlements['vodSubscription']:
      #     return True
      #return False
      return self.is_subscribed_channel(products)

    def get_channels(self):
      demarcation = self.account['demarcation']
      profile = self.account['platform']
      cache_filename = 'channels_{}.json'.format(self.quality)
      content = self.cache.load(cache_filename)
      if content:
        data = json.loads(content)
      else:
        url = self.endpoints['canales'].format(deviceType='webplayer', profile=profile, mdrm='true', demarcation=demarcation)
        if self.quality == 'UHD': url += '&filterQuality=UHD'
        #LOG(url)
        data = self.net.load_data(url)
        if not 'error' in data:
          self.cache.save_file(cache_filename, json.dumps(data, ensure_ascii=False))

      res = []
      if 'error' in data: return res

      for c in data:
        t = {}
        t['info'] = {}
        t['art'] = {}
        t['type'] = 'movie'
        t['stream_type'] = 'tv'
        t['info']['mediatype'] = 'movie'
        t['channel_name'] = c['Nombre'].strip()
        t['info']['title'] = str(c.get('Dial', '0')) +'. ' + t['channel_name']
        t['id'] = c['CodCadenaTv']
        t['cas_id'] = c.get('CasId')
        #if add_epg_info:
        #  t['desc1'] = c['Nombre']
        #  t['desc2'] = ''
        t['dial'] = c.get('Dial', '0')
        t['url'] = c['PuntoReproduccion']
        if 'Logo' in c:
          t['art']['icon'] = t['art']['thumb'] = t['art']['poster'] = c['Logo']
        elif 'Logos' in c:
          t['art']['icon'] = t['art']['thumb'] = t['art']['poster'] = c['Logos'][0]['uri']
        t['session_request'] = '{"contentID":"'+ t['id'] +'", "streamType":"CHN"}'
        t['subscribed'] = self.is_subscribed_channel(c.get('tvProducts', []))
        t['info']['playcount'] = 1 # Set as watched
        # epg
        #if add_epg_info:
        #  program = c['Pases'][0]
        #  t['desc1'] = program['Titulo']
        #  if 'TituloHorLinea2' in program:
        #    t['desc2'] = program['TituloHorLinea2']
        #  t['start'] = int(program['FechaHoraInicio'])
        #  t['end'] = int(program['FechaHoraFin'])
        #  t['start_str'] = timestamp2str(t['start'])
        #  t['end_str'] = timestamp2str(t['end'])
        #  t['info']['plot'] = '[B]{}-{}[/B] {}\n{}'.format(t['start_str'], t['end_str'], t['desc1'], t['desc2'])

        res.append(t)

      return res

    def get_channels_with_epg(self):
      channels = self.get_channels()
      epg = self.get_epg(duration=1)
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

    def add_to_wishlist(self, id, stype='vod'):
      LOG('add_to_wishlist: {} {}'.format(id, stype))
      url = self.endpoints['marcadofavoritos2'].format(family=stype)
      headers = self.net.headers.copy()
      headers['Accept'] = 'application/vnd.miviewtv.v1+json'
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = self.account['session_token']
      post_data = {'objectID': id}
      response = self.net.session.post(url, data=json.dumps(post_data), headers=headers)
      content = response.content.decode('utf-8')
      if response.status_code != 201:
        data = json.loads(content)
        if 'resultCode' in data:
          return data['resultCode'], data['resultText']
      return response.status_code, ''

    def delete_from_wishlist(self, id, stype='vod'):
      url = self.endpoints['borradofavoritos'].format(family=stype, contentId=id)
      headers = self.net.headers.copy()
      headers['Accept'] = 'application/vnd.miviewtv.v1+json'
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = self.account['session_token']
      response = self.net.session.delete(url, headers=headers)
      content = response.content.decode('utf-8')
      if response.status_code != 204:
        data = json.loads(content)
        if 'resultCode' in data:
          return data['resultCode'], data['resultText']
      return response.status_code, ''

    def get_wishlist_url(self):
      url = self.endpoints['favoritos'].format(
              deviceType=self.dplayer, DIGITALPLUSUSERIDC=self.account['encoded_user'], PROFILE=self.account['platform'],
              ACCOUNTNUMBER=self.account['id'], idsOnly='false', start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
      #url += '&filter=AD-SINX&topic=CN'
      if self.quality == 'UHD': url += '&filterQuality=UHD'
      url += '&_='+ str(int(time.time()*1000))
      return url

    def get_recordings_url(self):
      url = self.endpoints['grabaciones'].format(
              deviceType=self.dplayer, DIGITALPLUSUSERIDC=self.account['encoded_user'], PROFILE=self.account['platform'],
              idsOnly='false', start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
      #url += '&state=Completed&_='+ str(int(time.time()*1000))
      url += '&_='+ str(int(time.time()*1000))
      return url

    def get_viewings_url(self):
      url = self.endpoints['ultimasreproducciones'].format(
              deviceType=self.dplayer, DIGITALPLUSUSERIDC=self.account['encoded_user'], PROFILE=self.account['platform'],
              ACCOUNTNUMBER=self.account['id'], idsOnly='false', start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
      url += '&filter=AD-SINX'
      url += '&_='+ str(int(time.time()*1000))
      return url

    def get_search_url(self, search_term):
      url = self.endpoints['buscar_best'].format(
                 deviceType=self.dplayer,
                 ACCOUNTNUMBER=self.account['id'],
                 profile=self.account['platform'],
                 texto=search_term,
                 distilledTvRights=','.join(self.entitlements['distilledTvRights']),
                 mdrm='true', demarcation=self.account['demarcation'])
      if self.quality == 'UHD': url += '&filterQuality=UHD'
      return url

    def add_search(self, search_term):
      self.search_list.append(search_term)
      self.cache.save_file('searchs.json', json.dumps(self.search_list, ensure_ascii=False))

    def delete_search(self, search_term):
      self.search_list = [s for s in self.search_list if s != search_term]
      self.cache.save_file('searchs.json', json.dumps(self.search_list, ensure_ascii=False))

    def get_favorite_data(self, links):
      res = {}
      for link in links:
        name = link['rel']
        if 'favorites' in name:
          d = {}
          d['id'] = link['id']
          d['family'] = link.get('href', '').split("/")[-2]
          res[name] = d
      return res

    def get_ficha_url(self, id, mode='GLOBAL', catalog=''):
      url = self.endpoints['ficha'].format(deviceType=self.dplayer, id=id, profile=self.account['platform'], mediatype='FOTOV', version='7.1', mode=mode, catalog=catalog, channels='', state='', mdrm='true', demarcation=self.account['demarcation'], legacyBoxOffice='')
      url = url.replace('state=&', '')
      if self.quality == 'UHD': url += '&filterQuality=UHD'
      #print(url)
      return url

    def get_title(self, data):
      t = {}
      t['info'] = {}
      t['art'] = {}
      ed = data['DatosEditoriales']
      t['id'] = ed['Id']
      t['info']['title'] = ed['Titulo']
      t['art']['poster'] = ed.get('Imagen', '').replace('ywcatalogov', 'dispficha')
      if 'Imagenes' in ed:
        for i in ed['Imagenes']:
          if i['id'] == 'detail':
            t['art']['poster'] = i['uri']
      t['art']['thumb'] = t['art']['poster']
      t['info']['genre'] = ed['GeneroComAntena']
      if ed.get('TipoComercial') == 'Impulsivo': return None # Alquiler
      if 'Seguible' in ed: t['seguible'] = ed['Seguible']
      if 'links' in data:
        #t['links'] = data['links']
        t['favorite_data'] = self.get_favorite_data(data['links'])
      if ed['TipoContenido'] in ['Individual', 'Episodio']:
        t['type'] = 'movie'
        t['stream_type'] = 'vod'
        t['info']['mediatype'] = 'movie'
        t['info']['duration'] = ed['DuracionEnSegundos']
        t['url'] = ''
        t['session_request'] = ''
        if len(data['VodItems']) > 0:
          video = data['VodItems'][0]
          t['subscribed'] = self.is_subscribed_vod(video.get('tvProducts', []))
          if not 'UrlVideo' in video: return None
          t['url'] = video['UrlVideo']
          t['availability'] = {'start': video.get('FechaInicioPublicacion'), 'end': video.get('FechaFinPublicacion')}
          if video['AssetType'] == 'VOD':
            t['session_request'] = '{"contentID":' + str(t['id']) + ',"drmMediaID":"' + video['CasId'] +'", "streamType":"AST"}'
          elif video['AssetType'] == 'U7D':
            t['stream_type'] = 'u7d'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"CUTV"}'
          elif video['AssetType'] == 'NPVR':
            t['stream_type'] = 'rec'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"NPVR"}'
          if 'ShowId' in video: t['show_id'] = video['ShowId']
          if self.add_extra_info:
            self.add_video_extra_info(t)
        elif 'Pases' in data and len(data['Pases']) > 0:
          video = data['Pases'][0]
          t['subscribed'] = self.is_subscribed_vod(video.get('tvProducts', []))
          if 'ShowId' in video: t['show_id'] = video['ShowId']
          if 'Canal' in video and 'CasId' in video['Canal']:
            t['cas_id'] = video['Canal']['CasId']
          stype = None
          if 'catalog=catchup' in ed['Ficha']:
            stype = 'catch-up'
            t['stream_type'] = 'u7d'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"CUTV"}'
          elif 'catalog=npvr' in ed['Ficha']:
            stype = 'npvr'
            t['stream_type'] = 'rec'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"NPVR"}'
          if 'UrlVideo' in video:
            t['url'] = video['UrlVideo']
          else:
            if stype:
              for l in video['links']:
                if l['rel'] == stype:
                  t['url'] = l['href']
                  break
        if 'Recording' in data:
          t['stream_type'] = 'rec'
          t['rec'] = {'id': data['Recording']['id'],
                      'name': data['Recording']['name'],
                      'start': data['Recording']['beginTime'],
                      'end': data['Recording']['endTime']}
          if t['url'] == '': t['info']['title'] += ' (' + isodate2str(t['rec']['start']) + ')'
        if t['url'] == '' and t['stream_type'] == 'vod': t['subscribed'] = False
      if ed['TipoContenido'] == 'Serie':
        t['type'] = 'series'
        t['info']['mediatype'] = 'tvshow'
        t['subscribed'] = self.is_subscribed_vod(data.get('tvProducts', []))
      if ed['TipoContenido'] == 'Temporada':
        t['type'] = 'season'
        t['info']['mediatype'] = 'season'
        t['subscribed'] = self.is_subscribed_vod(data.get('tvProducts', []))
      if 'DatosAccesoAnonimo' in data:
        da = data['DatosAccesoAnonimo']
        t['video_format'] = da.get('FormatoVideo')
        if 'HoraInicio' in da and da['HoraInicio'] != None:
          t['start'] = int(da['HoraInicio'])
          t['start_str'] = timestamp2str(t['start'])
          t['date_str'] = timestamp2str(t['start'], '%a %d %H:%M')
          if t['url'] == '': t['info']['title'] += ' (' + t['date_str'] +')'
      return t

    def get_list(self, data):
      res = []
      for d in data:
        #print_json(d)
        t = self.get_title(d)
        if t and t['id'] != '':
          res.append(t)
      return res

    def add_video_extra_info(self, t):
      #LOG('add_video_extra_info: t: {}'.format(t))
      try:
        if 'show_id' in t:
          catalog = 'events'
          id = t['show_id']
        elif 'id' in t:
          catalog = ''
          id = t['id']
        else:
          return
        #LOG('id: {} catalog: {}'.format(id, catalog))

        prefix = 'event' if catalog=='events' else 'info'
        cache_filename = 'cache/{}_{}.json'.format(prefix, id)
        content = self.cache.load(cache_filename, 30*24*60)
        if content:
          data = json.loads(content)
        else:
          url = self.get_ficha_url(id=id, catalog=catalog)
          #print(url)
          data = self.net.load_data(url)
          self.cache.save_file(cache_filename, json.dumps(data, ensure_ascii=False))

        if not 'info' in t: t['info'] = {}
        if not 'art' in t: t['art'] = {}

        if not t['info'].get('title'):
          if 'TituloEpisodio' in data:
            t['info']['title'] = data['TituloEpisodio']
          else:
            t['info']['title'] = data['Titulo']

        if 'Serie' in data:
          if not t['info'].get('episode'): t['info']['episode'] = data['NumeroEpisodio']
          if not t['info'].get('tvshowtitle'): t['info']['tvshowtitle'] = data['Serie']['TituloSerie']
          if not t['info'].get('season') and data['Serie'].get('Temporada'):
            m = re.search(r'T(\d+)', data['Serie']['Temporada'])
            if m: t['info']['season'] = m.group(1)

        if not 'duration' in t['info']:
          t['info']['duration'] = data.get('Duracion', 0) * 60

        if data.get('Sinopsis'):
          t['info']['plot'] = data['Sinopsis']
        if data.get('Actores'):
          t['info']['cast'] = data['Actores'].split(', ')
        if data.get('Directores'):
          t['info']['director'] = data['Directores'].split(', ')
        if data.get('Anno'):
          t['info']['year'] = data['Anno']
        if data.get('Nacionalidad'):
          t['info']['country'] = data['Nacionalidad']
        im_thumb = im_default = im_season = im_fanart = None
        for im in data['Imagenes']:
          if im['id'] == 'horizontal': im_thumb = im['uri']
          elif im['id'] == 'default': im_default = im['uri']
          elif im['id'] == 'watch2tgr-end': im_fanart = im['uri']
          elif im['id'] == 'temporada': im_season = im['uri']
        if im_thumb and not t['art'].get('thumb'): t['art']['thumb'] = im_thumb
        if im_season:
          if not t['art'].get('poster'): t['art']['poster'] = im_season
        if im_fanart:
          if not t['art'].get('fanart'): t['art']['fanart'] = im_fanart
        if im_default:
          if not t['art'].get('poster'): t['art']['poster'] = im_default
          if not t['art'].get('icon'): t['art']['icon'] = im_default
          if not t['art'].get('fanart'): t['art']['fanart'] = im_default
      except:
        pass

    def get_seasons(self, id):
      url = self.get_ficha_url(id)
      #print(url)
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
        if 'Imagen' in data:
          t['art']['poster'] = t['art']['thumb'] = data['Imagen']
        elif 'Imagenes' in data:
          for im in data['Imagenes']:
            if im['id'] == 'ver-details': t['art']['poster'] = im['uri']
        t['subscribed'] = self.is_subscribed_vod(data.get('tvProducts', []))
        if 'Seguible' in data: t['seguible'] = data['Seguible']
        #t['video_format'] = data.get('FormatoVideo')
        c += 1
        res.append(t)

      return res

    def get_episodes(self, id):
      url = self.get_ficha_url(id=str(id))
      #print(url)
      data = self.net.load_data(url)
      #print_json(data)
      #Movistar.save_file('/tmp/episodes.json', json.dumps(data, ensure_ascii=False))
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
        t['info']['tvshowtitle'] = data.get('TituloSerie', '')
        if 'Imagen' in data:
          t['art']['poster'] = data['Imagen']
        elif 'Imagenes' in data:
          for im in data['Imagenes']:
            if im['id'] == 'ver-details': t['art']['poster'] = im['uri']
        for im in ed['Imagenes']:
          if im['id'] == 'horizontal': t['art']['thumb'] = im['uri']
        t['info']['season'] = '0'
        if ed.get('Temporada'):
          m = re.search(r'T(\d+)', ed['Temporada'])
          if m: t['info']['season'] = m.group(1)
        t['url'] = ''
        t['session_request'] = ''
        if len(d['VodItems']) > 0:
          video = d['VodItems'][0]
          #if video.get('AssetType') == 'SOON': continue
          if not 'UrlVideo' in video: continue
          t['subscribed'] = self.is_subscribed_vod(video.get('tvProducts', []))
          t['url'] = video['UrlVideo']
          t['availability'] = {'start': video.get('FechaInicioPublicacion'), 'end': video.get('FechaFinPublicacion')}
          if video['AssetType'] == 'VOD':
            t['session_request'] = '{"contentID":' + str(t['id']) + ',"drmMediaID":"' + video['CasId'] +'", "streamType":"AST"}'
          elif video['AssetType'] == 'U7D':
            t['stream_type'] = 'u7d'
            t['session_request'] = '{"contentID":' + str(t['id']) + ', "streamType":"CUTV"}'
          if 'ShowId' in video: t['show_id'] = video['ShowId']
        if 'DatosAccesoAnonimo' in d:
          da = d['DatosAccesoAnonimo']
          t['video_format'] = da.get('FormatoVideo')
          if 'HoraInicio' in da and da['HoraInicio'] != None:
            t['start'] = int(da['HoraInicio'])
            t['start_str'] = timestamp2str(t['start'])
            t['date_str'] = timestamp2str(t['start'], '%a %d %H:%M')
            if t['url'] == '': t['info']['title'] += ' (' + t['date_str'] +')'
        if self.add_extra_info:
          self.add_video_extra_info(t)
        res.append(t)

      return res

    def get_u7d_url(self, url):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-HZId'] = self.account['session_token']
      data = self.net.load_data(url, headers)
      return data

    def order_recording(self, program_id):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = self.account['session_token']
      url = self.endpoints['grabarprograma']
      data = '{"tvProgramID":"' + str(program_id) +'"}'
      response = self.net.session.post(url, data=data, headers=headers)
      content = response.content.decode('utf-8')
      try:
        data = json.loads(content)
        return data
      except:
        return None

    def order_recording_season(self, season_id):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = self.account['session_token']
      url = self.endpoints['grabartemporada']
      data = '{"tvSeasonID":"' + str(season_id) +'"}'
      response = self.net.session.post(url, data=data, headers=headers)
      content = response.content.decode('utf-8')
      try:
        data = json.loads(content)
        return data
      except:
        return None

    def delete_recording(self, program_id):
      headers = self.net.headers.copy()
      headers['Content-Type'] = 'application/json'
      headers['X-Hzid'] = self.account['session_token']
      url = self.endpoints['borrargrabacionindividual'].format(showId=program_id)
      response = self.net.session.delete(url, headers=headers)
      content = response.content.decode('utf-8')
      try:
        data = json.loads(content)
        return data
      except:
        return None

    def epg_to_movies(self, channel_id, date=None, duration=2):
      LOG('epg_to_movies: {} {}'.format(channel_id, date))
      epg = self.get_epg(channels=channel_id, date=date, duration=duration)
      res = []
      if not channel_id in epg: return res
      for p in epg[channel_id]:
        if sys.version_info[0] < 3:
          p['date_str'] = unicode(p['date_str'], 'utf-8')
        name = '[B]' + p['date_str'] + '[/B] ' + p['desc1']
        if p['desc2']: name += ' - '+ p['desc2']
        plot = name +"\n" + p['desc2']
        t = {'info': {}, 'art': {}}
        t['info']['title'] = name
        t['info']['plot'] = plot
        t['type'] = 'movie'
        t['stream_type'] = 'u7d'
        t['info']['mediatype'] = 'movie'
        t['url'] = ''
        t['id'] = p['id']
        t['show_id'] = p['show_id']
        if 'serie_id' in p:
          t['serie_id'] = p['serie_id']
        t['session_request'] = '{"contentID":' + str(t['id']) +',"streamType":"CUTV"}'
        t['info']['playcount'] = 1 # Set as watched
        t['start'] = p['start']
        t['end'] = p['end']
        t['aired'] = (p['end'] <= (time.time() * 1000))
        t['subscribed'] = True # Fix me
        """
        if 'links' in p:
          for link in p['links']:
            if link['rel'] == 'start-over':
              t['url'] = link['href']
        """
        t['url'] = 'https://grmovistar.imagenio.telefonica.net/asfe/rest/tvMediaURLs?tvProgram.id='+ str(t['show_id']) +'&svc=startover'
        if self.add_extra_info:
          self.add_video_extra_info(t)
        res.append(t)
      return res

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
      #sort = 'FE'
      sort = 'MA'
      #sort = 'AZ'
      url = self.endpoints['consultar'].format(deviceType=self.dplayer, profile=self.account['platform'], sort=sort, start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
      filter = '&filter=AC-OM,AC-MA,MA-GBLCICLO59,TD-CUP,RG-SINCAT,AC-PREPUB,' + self.entitlements['suscripcion']
      #filter = '&filter=AC-OM,AC-MA,MA-GBLCICLO59,TD-CUP,RG-SINCAT,AC-PREPUB'
      url += '&mode=VOD' + filter
      if cat == 'tvshows':
        url += '&topic=SR&showSeries=series'
      elif cat == 'movies':
        url += '&topic=CN'
      elif cat == 'documentaries':
        url += '&topic=DC'
      elif cat == 'kids':
        url += '&topic=IN'
      if self.quality == 'UHD': url += '&filterQuality=UHD'
      #LOG('vod url: {}'.format(url))
      return url

    def get_vod_sections(self):
      from collections import OrderedDict

      profile = self.account['platform']
      #profile = 'OTT'
      #profile = 'LITE'

      content = self.cache.load('vod_sections2.json')
      if content:
        data = json.loads(content)
      else:
        url = 'https://ottcache.dof6.com/movistarplus/yomvi/phone.android/{}/configuration/config_item?format=json&uisegment='.format(profile)
        data = self.net.load_data(url)
        self.cache.save_file('vod_sections2.json', json.dumps(data, ensure_ascii=False))

      main_menu_items = []
      main_menu = data.get('VOD', {}).get('Menu', [])
      for m in main_menu:
        if m['@id'] == 'MENU-PRINCIPAL':
          for i in m['Item']:
            main_menu_items.append(i['@id'])

      submenu = data.get('VOD', {}).get('Submenu', [])
      res = OrderedDict()
      for o in submenu:
        #print_json(o)
        menu = {}
        menu['visible'] = True
        menu['id'] = o.get('@id')
        if menu['id'] not in main_menu_items: continue

        if 'Modulo' in o:
          section_name = o['@nombre'] if '@nombre' in o else o['@P'] if '@P' in o else 'sin nombre'
          #print(section_name)
          modulo = o['Modulo']

          section = []

          if isinstance(modulo, dict):
            modulo = [modulo]

          if isinstance(modulo, list):
            for m in modulo:

              sort = ''
              if 'Modificador' in m:
                #print(m['Modificador'])
                for p in m['Modificador']:
                  #print(p)
                  #if p['@type'] == 'novisible': continue
                  if p['@id'] == 'ordenacion': sort = p['@selected']

              if 'consulta' in m and m['consulta'].get('@endpoint_ref', '') == 'consultar':
                if not '@nombre' in m: continue
                #print (menu['id'], m['@nombre'])
                c = {}
                c['name'] = m['@nombre']
                pars = ''

                parametros = m['consulta']['parametro']
                if isinstance(parametros, dict):
                  parametros = [parametros]

                for par in parametros:
                  #print_json(par)
                  pars += '&{}={}'.format(par['@id'], par['@value'])

                pars = pars.replace('{suscripcion}', self.entitlements['suscripcion'])
                c['url'] = self.endpoints['consultar'].format(deviceType=self.dplayer, profile=profile, sort=sort, start=1, end=50, mdrm='true', demarcation=self.account['demarcation'])
                c['url'] += pars
                #print(c['url'])
                if self.quality == 'UHD': c['url'] += '&filterQuality=UHD'
                section.append(c)
          if len(section) > 0:
            menu['name'] = section_name
            menu['data'] = section
            res[menu['id']] = menu

      return res

    def install_key_file(self, filename):
      if sys.version_info[0] > 2:
        filename = bytes(filename, 'utf-8')
      shutil.copyfile(filename, self.cache.config_directory + 'auth.key')

    def export_key_file(self, filename):
      if sys.version_info[0] > 2:
        filename = bytes(filename, 'utf-8')
      if self.account['access_token']:
        data = {'timestamp': int(time.time()*1000),
                'response':{'access_token': self.account['access_token'], 'token_type': 'bearer'}};
        with io.open(filename, 'w', encoding='utf-8', newline='') as handle:
         handle.write(json.dumps(data, ensure_ascii=False))
      else:
        shutil.copyfile(self.cache.config_directory + 'auth.key', filename)

    def load_key_file(self):
      content = self.cache.load_file('auth.key')
      if content:
        data = json.loads(content)
        if 'response' in data:
          self.account['access_token'] = data['response']['access_token']
        elif 'data' in data:
          data = json.loads(data['data'])
          self.account['access_token'] = data['response']['access_token']

    def save_key_file(self, d):
      data = {'timestamp': int(time.time()*1000), 'response': d}
      self.cache.save_file('auth.key', json.dumps(data, ensure_ascii=False))

    def import_credentials(self, filename):
      if sys.version_info[0] > 2:
        filename = bytes(filename, 'utf-8')
      shutil.copyfile(filename, self.cache.config_directory + 'credentials.json')

    def export_credentials(self, filename):
      if sys.version_info[0] > 2:
        filename = bytes(filename, 'utf-8')
      shutil.copyfile(self.cache.config_directory + 'credentials.json', filename)

    def delete_session_files(self):
      for f in ['access_token.conf', 'account.json', 'device_id.conf', 'devices.json', 'profile_id.conf', 'tokens.json', 'channels2.json', 'channels_UHD.json', 'channels_HD.json', 'epg2.json', 'epg_UHD.json', 'epg_HD.json']:
        self.cache.remove_file(f)

    def get_profile_image_url(self, img_id):
      content = self.cache.load_file('avatars.json')
      if content:
        data = json.loads(content)
      else:
        url = self.endpoints['avatares']
        data = self.net.load_data(url)
        self.cache.save_file('avatars.json', json.dumps(data, ensure_ascii=False))
      #print_json(data)
      for avatar in data:
        if avatar['id'] == img_id:
          for link in avatar['links']:
            if link['sizes'] == '512x512':
              return link['href']
      return None

    def export_channels(self):
      if sys.version_info[0] >= 3:
        from urllib.parse import urlencode
      else:
        from urllib import urlencode
      channels = self.get_channels()
      res = []
      for c in channels:
        t = {}
        t['subscribed'] = c['subscribed']
        t['name'] = c['channel_name']
        t['id'] = c['id']
        t['logo'] = c['art']['icon']
        t['preset'] = c['dial']
        args = urlencode({'action': 'play', 'stype': 'tv', 'id': c['id'], 'url': c['url'], 'session_request': c['session_request']})
        t['stream'] = 'plugin://plugin.video.movistarplus/?' + args
        if 'cas_id' in c: t['cas_id'] = c['cas_id']
        res.append(t)
      return res

    def export_channels_to_m3u8(self, filename, only_subscribed=False):
      channels = self.export_channels()
      items = []
      for t in channels:
        if only_subscribed and not t['subscribed']: continue
        url = t['stream']
        if 'cas_id' in t: url += '&cas_id=' + t['cas_id']
        item = '#EXTINF:-1 tvg-name="{name}" tvg-id="{id}" tvg-logo="{logo}" tvg-chno="{preset}" group-title="Movistar+",{name}\n{stream}\n\n'.format(
            name=t['name'], id=t['id'], logo=t['logo'], preset=t['preset'], stream=url)
        items.append(item)
      res = '#EXTM3U\n## Movistar+\n{}'.format(''.join(items))
      with io.open(filename, 'w', encoding='utf-8', newline='') as handle:
        handle.write(res)

    def export_epg(self, date=None, duration=2):
      if sys.version_info[0] >= 3:
        from urllib.parse import urlencode
      else:
        from urllib import urlencode

      res = {}
      epg = self.get_epg(date, duration)
      channels = self.get_channels()
      for channel in channels:
        id = channel['id']
        if not id in epg: continue
        res[id] = []
        for e in epg[id]:
          t = {}
          t['title'] = e['desc1']
          t['subtitle'] = e['desc2']
          t['start'] = datetime.utcfromtimestamp(e['start']/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
          t['stop'] = datetime.utcfromtimestamp(e['end']/1000).strftime('%Y-%m-%dT%H:%M:%SZ')

          if True:
            program_id = str(e['show_id'])
            url = 'https://grmovistar.imagenio.telefonica.net/asfe/rest/tvMediaURLs?tvProgram.id='+ program_id +'&svc=startover'
            session_request = '{"contentID":' + program_id +',"streamType":"CUTV"}'
            args = urlencode({'action': 'play', 'stype': 'u7d', 'id': program_id, 'url': url, 'session_request': session_request})
            t['stream'] = 'plugin://plugin.video.movistarplus/?' + args

          if False and self.add_extra_info and id in ['HOLLYW', 'TCM', 'AMC', 'MV3', 'MV2', 'CPSER', 'FOXGE', 'TNT']:
            i = {'id': e['id'], 'show_id': e['show_id']}
            self.add_video_extra_info(i)
            #print(i)
            t['description'] = i['info'].get('plot')
            t['image'] = i['art'].get('poster')
            t['credits'] = []
            for text in i['info'].get('director', []):
              t['credits'].append({'type': 'director', 'name': text})
            for text in i['info'].get('cast', []):
              t['credits'].append({'type': 'actor', 'name': text})

          res[id].append(t)
      return res

    def export_epg_to_xml(self, filename, ndays=3, report_func=None, only_subscribed=False):
      if sys.version_info[0] < 3:
        # Python 2
        from cgi import escape as html_escape
      else:
        # Python 3
        from html import escape as html_escape

      channels = self.export_channels()
      res = []
      res.append('<?xml version="1.0" encoding="UTF-8"?>\n' + 
                 '<!DOCTYPE tv SYSTEM "xmltv.dtd">\n' + 
                 '<tv>\n')

      for t in channels:
        if only_subscribed and not t['subscribed']: continue
        res.append('<channel id="{}">\n'.format(t['id']) + 
                  '  <display-name>{}</display-name>\n'.format(t['name']) + 
                  '  <icon src="{}"/>\n'.format(t['logo']) + 
                  '</channel>\n')

      if True:
        epg = {}
        today = datetime.today()
        total_items = 0
        for i in range(0, ndays, 1):
          date = today + timedelta(days=i)
          strdate = date.strftime('%Y-%m-%dT00:00:00')
          LOG('epg: {}'.format(strdate))
          if report_func:
            report_func(date.strftime('%d/%m/%Y'))
          e = self.export_epg(strdate, 1)
          LOG('epg: channels: {}'.format(len(e)))
          for ch in e:
            if not ch in epg: epg[ch] = []
            total_items += len(e[ch])
            epg[ch].extend(e[ch])
          LOG('epg: total items: {}'.format(total_items))
      else:
        epg = self.export_epg()

      for ch in channels:
        if not ch['id'] in epg: continue
        if only_subscribed and not ch['subscribed']: continue
        for e in epg[ch['id']]:
          #LOG('* e:{}'.format(e))
          start = datetime.strptime(e['start'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H%M%S +0000")
          stop = datetime.strptime(e['stop'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d%H%M%S +0000")
          url = e.get('stream', None)
          if url:
            url = url.replace('&', '&amp;')
          res.append('<programme start="{}" stop="{}" channel="{}"'.format(start, stop, ch['id']) +
                    #(' catchup-id="{}"'.format(url) if url else "") +
                    '>\n' +
                    '  <title>{}</title>\n'.format(html_escape(e['title'])) +
                    '  <sub-title>{}</sub-title>\n'.format(html_escape(e['subtitle'])))
          if 'image' in e:
            res.append('  <icon src="{}"/>\n'.format(e['image']))
          if 'description' in e:
            res.append('  <desc>{}</desc>\n'.format(html_escape(e['description'])))
          if 'credits' in e and len(e['credits']) > 0:
            res.append('  <credits>\n');
            for c in e['credits']:
              if c['type'] == 'director':
                res.append('    <director>{}</director>\n'.format(c['name']))
              elif c['type'] == 'actor':
                res.append('    <actor>{}</actor>\n'.format(c['name']))
            res.append('  </credits>\n');
          res.append('</programme>\n')
      res.append('</tv>\n')
      with io.open(filename, 'w', encoding='utf-8', newline='') as handle:
        handle.write(''.join(res))

    def save_credentials(self, username, password):
      from .b64 import encode_base64
      data = {'username': username, 'password': encode_base64(password)}
      self.cache.save_file('credentials.json', json.dumps(data, ensure_ascii=False))

    def load_credentials(self):
      from .b64 import decode_base64
      content = self.cache.load_file('credentials.json')
      if content:
        data = json.loads(content)
        return data['username'], decode_base64(data['password'])
      else:
        return '', ''

    def get_token_properties(self, token=None):
      from .b64 import decode_base64
      if not token:
        token = self.account['access_token']
      data = None
      try:
        l = token.split('.')
        if len(l) > 1:
          padding = len(l[1]) % 4
          l[1] += '=' * (4 - padding) if padding != 0 else ''
          s = decode_base64(l[1])
          data = json.loads(s)
      except:
        pass
      return data

    def get_token_expire_date(self, token):
      data = self.get_token_properties(token)
      return data.get('exp', 0)

    def get_accounts(self):
      accounts = []
      for d in os.listdir(self.config_dir):
        if os.path.isdir(os.path.join(self.config_dir, d)) and d.startswith("account_"):
          account = {'id': d, 'name': d.replace('account_', 'Cuenta ')}
          content = Movistar.load_file_if_exists(os.path.join(self.config_dir, d, 'account.json'))
          if content:
            data = json.loads(content)
            login = data.get('login')
            if login:
              if '@' in login:
                p1, p2 = login.split('@')
                account['login'] = p1[:3] +'...@'+ p2
              else:
                account['login'] = login[:3]
          accounts.append(account)
      return accounts

    def switch_account(self, name):
      Movistar.save_file(self.config_dir + 'account.txt', name)

    def create_new_account(self):
      accounts = self.get_accounts()
      name = None
      n = 1
      while True:
        name = 'account_' + str(n)
        if not any(account.get("id") == name for account in accounts):
          break;
        n += 1
      if name:
        os.makedirs(self.config_dir + name)
      return name

    @staticmethod
    def load_file_if_exists(filename):
      content = None
      if os.path.exists(filename):
        with io.open(filename, 'r', encoding='utf-8') as handle:
          content = handle.read()
      return content

    @staticmethod
    def save_file(filename, content):
      if sys.version_info[0] < 3:
        if not isinstance(content, unicode):
          content = unicode(content, 'utf-8')
      with io.open(filename, 'w', encoding='utf-8') as handle:
        handle.write(content)
