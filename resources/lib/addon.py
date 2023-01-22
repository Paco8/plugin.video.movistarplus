#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:  # Kodi >= 19
  from xbmcvfs import translatePath
except ImportError:  # Kodi 18
  from xbmc import translatePath

import os
import xbmcaddon
from .log import LOG

addon = xbmcaddon.Addon()
profile_dir = translatePath(addon.getAddonInfo('profile'))

LOG("Profile directory: {}".format(profile_dir))
if not os.path.exists(profile_dir):
  LOG('Creating {}'.format(profile_dir))
  os.makedirs(profile_dir)
