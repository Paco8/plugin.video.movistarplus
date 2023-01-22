#!/usr/bin/env python
# encoding: utf-8
#
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import unicode_literals, absolute_import, division

import io
import re

with io.open('addon.xml', 'r', encoding='utf-8') as handle:
  text = handle.read()
  m = re.search(r'movistar.*?version="(.*?)"', text, re.DOTALL)
  if m:
    print(m.group(1))


