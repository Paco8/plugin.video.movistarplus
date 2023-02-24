# -*- coding: utf-8 -*-
"""IPTV Manager Integration module"""

import json
import socket
from .movistar import Movistar

class IPTVManager:
    """Interface to IPTV Manager"""

    def __init__(self, port):
        """Initialize IPTV Manager object"""
        self.port = port

    def via_socket(func):
        """Send the output of the wrapped function to socket"""

        def send(self, m):
            """Decorator to send over a socket"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self, m)).encode())
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self, m):
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        return dict(version=1, streams=m.export_channels())

    @via_socket
    def send_epg(self, m):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        return dict(version=1, epg=m.export_epg())
