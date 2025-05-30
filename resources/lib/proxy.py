#!/usr/bin/env python
# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

try:  # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

try:  # Python 3
    from socketserver import TCPServer, ThreadingMixIn
except ImportError:  # Python 2
    from SocketServer import TCPServer, ThreadingMixIn

try:  # Python 3
    from urllib.parse import unquote, quote_plus
except ImportError:  # Python 2
    from urllib import unquote, quote_plus

try:  # Python 3
  from urllib.parse import parse_qsl
except:  # Python 2
  from urlparse import parse_qsl

"""
try:  # Python 3
    from SocketServer import ThreadingTCPServer
except ImportError:  # Python 2
    from socketserver import ThreadingTCPServer
"""

import os
import re
import json
import requests
import threading
import socket
from contextlib import closing

from .b64 import encode_base64
from .log import LOG
from .mysession import MySession
from .addon import profile_dir, addon
from .useragent import useragent

from ttml2ssa import Ttml2SsaAddon
ttml = Ttml2SsaAddon()

session = MySession()
session.headers.update({'user-agent': useragent})
previous_tokens = []

reregister_needed = False

def is_ascii(s):
  try:
    return s.isascii()
  except:
    return all(ord(c) < 128 for c in s)

def try_load_json(text):
  try:
    return json.loads(text)
  except:
    return None

mvs_o = None
def mvs():
  global mvs_o
  if not mvs_o:
    from .movistar import Movistar
    reuse_devices = addon.getSettingBool('reuse_devices')
    mvs_o = Movistar(profile_dir, reuse_devices)
  return mvs_o


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle http get requests, used for manifest"""
        path = self.path  # Path with parameters received from request e.g. "/manifest?id=234324"
        print('HTTP GET Request received to {}'.format(path))
        try:
        #if True:
            if 'manifest' in path:
              pos = path.find('=')
              url = path[pos+1:]
              LOG('url: {}'.format(url))
              #LOG('request headers: {}'.format(self.headers))
              additional_headers = {}
              if 'x-tcdn-token' in self.headers:
                additional_headers['x-tcdn-token'] = self.headers['x-tcdn-token']
              #LOG('additional_headers: {}'.format(additional_headers))
              response = session.get(url, allow_redirects=True, headers=additional_headers)
              LOG('headers: {}'.format(response.headers))
              baseurl = os.path.dirname(response.url)
              LOG('baseurl: {}'.format(baseurl))
              content = response.content.decode('utf-8')

              if addon.getSettingBool('proxy_process_subs'):
                LOG(self.headers.get('Host'))
                my_address = 'http://' + self.headers.get('Host')
                LOG('my_address: {}'.format(my_address))
                content = content.replace('mimeType="application/ttml+xml"', 'mimeType="text/vtt"')
                content = re.sub(r'<BaseURL>(.*?)\.ttml<\/BaseURL>', r'<BaseURL>{}/?subtitle={}/\1.ttml</BaseURL>'.format(my_address, baseurl), content)

              pos = content.find('<Period id')
              if pos > -1:
                content = content[:pos] + '<BaseURL>' + baseurl + '/</BaseURL>' + content[pos:]

              if addon.getSettingBool('fix_languages'):
                replacements = {'qaa': 'eng', 'srd': 'es-[CC]', 'ads': 'es-[ADS]'}
                for key, value in replacements.items():
                  content = content.replace('lang="{}"'.format(key), 'lang="{}"'.format(value))
                content = re.sub(r'lang="q([^"]*)"', r'lang="es-[q\1]"', content)

              if addon.getSettingBool('delete_ec3_audio'):
                pattern = re.compile(r'<AdaptationSet[^>]*contentType="audio"[^>]*>.*?</AdaptationSet>', re.DOTALL)
                matches = pattern.findall(content)
                for match in matches:
                  if 'codecs="ec-3"' in match:
                    content = content.replace(match, "<!-- Deleted ec-3 audio track -->\n")

              # For U7D
              content = content.replace('timeShiftBufferDepth="PT3600S"', 'timeShiftBufferDepth="PT10800S"')

              #LOG('content: {}'.format(content))
              manifest_data = content
              self.send_response(200)
              #self.send_header('Content-type', 'application/xml')
              self.send_header('Content-type', 'text/plain')
              self.end_headers()
              self.wfile.write(manifest_data.encode('utf-8'))
            elif 'subtitle' in path:
              pos = path.find('=')
              url = path[pos+1:]
              LOG('subtitle url: {}'.format(url))
              response = session.get(url, allow_redirects=True)
              content = response.content
              ttml.parse_ttml_from_string(content)
              sub_data = ttml.generate_vtt()
              self.send_response(200)
              self.send_header('Content-type', 'text/plain')
              self.end_headers()
              self.wfile.write(sub_data.encode('utf-8'))
            elif 'fragment' in path:
              pos = path.find('=')
              url = path[pos+1:]
              LOG('url: {}'.format(url))
              self.send_response(301)
              self.send_header('Location', url)
              self.end_headers()
            else:
              self.send_response(404)
              self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            LOG('Exception error: {}'.format(str(e)))


    def do_POST(self):
        """Handle http post requests, used for license"""
        path = self.path  # Path with parameters received from request e.g. "/license?id=234324"
        print('HTTP POST Request received to {}'.format(path))
        if '/license' not in path:
            self.send_response(404)
            self.end_headers()
            return
        try:
        #if True:
            pos = path.find('?')
            path = path[pos+1:]
            params = dict(parse_qsl(path))
            LOG('params: {}'.format(params))

            length = int(self.headers.get('content-length', 0))
            isa_data = self.rfile.read(length)
            LOG('isa_data length: {}'.format(length))
            LOG('isa_data: {}'.format(encode_base64(isa_data)))

            token = params['token']
            LOG('token: {}'.format(token))

            global previous_tokens, reregister_needed
            while True:
              LOG('reregister_needed: {}'.format(reregister_needed))
              # Discard previous mvs_o, it may have expired tokens
              global mvs_o
              mvs_o = None
              if reregister_needed and addon.getSettingBool('reregister'):
                mvs().unregister_device()
                mvs().register_device()

              if token in previous_tokens and params['stype'] == 'vod':
                LOG('duplicated token')
                LOG('previous_tokens: {}'.format(previous_tokens))
                d = mvs().open_session(params['session_request'])
                LOG('Open session (proxy): d: {}'.format(d))
                if 'resultData' in d and 'cToken' in d['resultData']:
                  token = d['resultData']['cToken']
                  LOG('new token: {}'.format(token))
                session_response = mvs().delete_session()
                LOG('Delete session (proxy): {}'.format(session_response))
              previous_tokens.append(token)

              headers = {
              'User-Agent': useragent,
              'Accept': '*/*',
              'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
              'Referer': 'https://ver.movistarplus.es/',
              'nv-authorizations': quote_plus(token),
              'Origin': 'https://ver.movistarplus.es',
              }
              LOG('headers: {}'.format(headers))

              url = 'https://wv-ottlic-f3.imagenio.telefonica.net/TFAESP/wvls/contentlicenseservice/v1/licenses'
              response = session.post(url, data=isa_data, headers=headers)
              license_data = response.content
              LOG('license response length: {}'.format(len(license_data)))
              if is_ascii(license_data):
                LOG('license response: {}'.format(license_data))
                d = try_load_json(license_data)
                if d and 'errorCode' in d:
                  from .gui import show_notification
                  show_notification('Error {}: {}'.format(d['errorCode'], d['message']))
                  if d['errorCode'] == 4027:
                    if not reregister_needed and addon.getSettingBool('reregister'):
                      reregister_needed = True
                      continue
              else:
                LOG('license response: {}'.format(encode_base64(license_data)))
              break

            self.send_response(response.status_code)
            self.end_headers()
            self.wfile.write(license_data)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            LOG('Exception error: {}'.format(str(e)))


HOST = '127.0.0.1'
PORT = 57011

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class Proxy(object):
    started = False

    def check_port(self, port=0, default=False):
      try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
          s.bind((HOST, port))
          s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          return s.getsockname()[1]
      except:
        return default

    def start(self):
        if self.started:
            return

        port = self.check_port(PORT)
        if not port:
          port = self.check_port(0)
        LOG('port: {}'.format(port))

        self._server = ThreadedHTTPServer((HOST, port), RequestHandler)
        self._server.allow_reuse_address = True
        self._httpd_thread = threading.Thread(target=self._server.serve_forever)
        self._httpd_thread.start()
        self.proxy_address = 'http://{}:{}'.format(HOST, port)
        addon.setSetting('proxy_address', self.proxy_address)
        self.started = True
        LOG("Proxy Started: {}:{}".format(HOST, port))

    def stop(self):
        if not self.started:
            return

        self._server.shutdown()
        self._server.server_close()
        self._server.socket.close()
        self._httpd_thread.join()
        self.started = False
        LOG("Proxy: Stopped")
