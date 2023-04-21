#!/usr/bin/env python
# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import xbmc
from .log import LOG

class MyPlayer(xbmc.Player):

  def __init__(self):
    super(MyPlayer, self).__init__()
    self.running = True

  def onPlayBackEnded(self):
    LOG('onPlayBackEnded')
    self.finish()

  def onPlayBackError(self):
    LOG('onPlayBackError')
    self.finish()

  def onPlayBackStopped(self):
    LOG('onPlayBackStopped')
    self.finish()

  def finish(self):
    LOG('finish')
    self.running = False
