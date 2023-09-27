# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import xbmcgui
import xbmc
import xbmcaddon

class CustomDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.image = kwargs.get("image", "")
        #self.heading = kwargs.get("heading", "")
        self.text = kwargs.get("text", "")

    def onInit(self):
        self.imagecontrol = 501
        self.textbox = 502
        self.okbutton = 503
        self.heading = 504
        self.showdialog()

    def showdialog(self):
        self.getControl(self.imagecontrol).setImage(self.image)
        self.getControl(self.textbox).setText(self.text)
        #self.getControl(self.heading).setLabel(self.heading)
        self.setFocus(self.getControl(self.okbutton))

    def onClick(self, controlId):
        if (controlId == self.okbutton):
            self.close()

def show_donation_dialog():
    addon = xbmcaddon.Addon()
    try:
      CWD = addon.getAddonInfo('path').decode('utf-8')
    except:
      CWD = addon.getAddonInfo('path')
    image = 'qr.png'
    text = addon.getLocalizedString(30451)
    text += '[CR]https://www.buymeacoffee.com/addons'
    dialog = CustomDialog("customdialog.xml", CWD, 'default', '1080i', text=text, image=image)
    dialog.doModal()
