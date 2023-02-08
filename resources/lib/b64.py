# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import base64
import sys

if sys.version_info[0] >= 3:
    unicode = str

def encode_base64(data):
    if isinstance(data, unicode):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")

def decode_base64(data):
    if isinstance(data, unicode):
        data = data.encode("utf-8")
    return base64.b64decode(data).decode("utf-8")
