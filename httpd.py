#! /usr/bin/env python
# vim:ts=4:sw=4:et:

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import pywatchman
import argparse
import os
import sys
import time
import json


class WServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        try:
            self._set_headers()
            client = pywatchman.client(timeout=600)
            client.capabilityCheck(required=['cmd-watch-project', 'wildmatch'])
            resp = client.query("version");
            self.wfile.write(json.dumps(resp))
        except pywatchman.CommandError as ex:
            print('watchman:', str(ex), sys.stderr)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        try:
            p = json.loads(data)
            cmd = path = opts = None
            if len(p) == 3:
                (cmd, path, opts) = p
            elif len(p) == 2:
                (cmd, path) = p
            elif len(p) == 1:
                cmd = p[0]

            if cmd is None:
                cmd = "list-capabilities"

            client = pywatchman.client(timeout=600)
            resp = client.query(cmd, path, opts);
            self.wfile.write(json.dumps(resp))
        except pywatchman.CommandError as ex:
           self.wfile.write(json.dumps(str(ex)))
           print('watchman:', str(ex), sys.stderr)


def run(server_class=HTTPServer, handler_class=WServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print ("Starting httpd on [host=%s, port=%s] ..." % (os.uname()[1], port))
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
