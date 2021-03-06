#! /usr/bin/env python3

import time
import os
import argparse
import ssl
import re

from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote_plus

LOG_FILE = ".post.log"


class Server(BaseHTTPRequestHandler):
    # Update or create logfile
    def _update_logfile(self, type="POST",
                        ts=0.0,
                        dtime=datetime(1970, 1, 1),
                        whois="unknown",
                        data=""):
        self._logheader = "type,ts,datetime,user,data"
        self._logfilepath = LOG_FILE

        if not os.path.exists(self._logfilepath):
            file = open(self._logfilepath, 'w+')
            file.write(self._logheader + "\n")
            file.close()

        fts = "{0:.3f}".format(round(ts, 3))
        ftime = dtime.strftime("%d %b %Y %H:%M:%S.")
        ftime += str(round(int(dtime.strftime("%f")), -3))[:3]

        logstring = "{},{},{},{},{}".format(type,
                                            fts,
                                            ftime,
                                            whois,
                                            str(data))
        file = open(self._logfilepath, 'a')
        file.write(logstring + "\n")
        file.close()

    # Compose request info
    def _log_request(self, req_type, req_data, req_ip):
        ts = time.time()
        now = datetime.now()

        self._update_logfile(
            type=req_type,
            ts=ts,
            dtime=now,
            whois=req_ip,
            data=req_data
        )

    # POST callback
    def do_POST(self):
        req_data = self.rfile.read(int(self.headers['Content-Length']))
        req_data = req_data.decode('ascii')
        req_ip = self.client_address[0]

        self._log_request("POST", req_data, req_ip)

        self.send_response(200, message="OK")
        self.end_headers()

    # GET callback
    def do_GET(self):
        req_data = unquote_plus(urlparse(self.path).query)
        req_data = re.split(r'&callback=jQuery', req_data)[0]
        req_ip = self.client_address[0]

        self._log_request("GET", req_data, req_ip)

        self.send_response(200)
        self.end_headers()


class Logger(object):
    def __init__(self, port=9090, cert=None, key=None):
        self._port = port
        self._path_to_cert = cert
        self._path_to_key = key

    # Run server until KeyboardInterrupt
    def run(self):
        server_address = ('', self._port)
        server = HTTPServer(server_address, Server)

        # If certs are provided, convert socket to SSLSocket
        if self._path_to_cert is not None and self._path_to_key is not None:
            server.socket = ssl.wrap_socket(server.socket,
                                            certfile=self._path_to_cert,
                                            keyfile=self._path_to_key,
                                            server_side=True)

        start_time = time.time()
        print('Starting server')
        try:
            server.serve_forever()

        except OSError as e:
            print(e)

        except KeyboardInterrupt:
            pass

        server.shutdown()
        dtime = time.time() - start_time
        dtime_str = timedelta(seconds=dtime)

        print('Server is offline')
        print('Uptime is {}'.format(dtime_str))


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description='GET and POST HTTP Requests logger')
    p.add_argument('-P', '--port', type=int, help='port')
    p.add_argument('-L', '--logfile', type=str, default=".data.log",
                   help='Path to logfile')
    p.add_argument('-S', '--SSLcert', type=str, help='Path to SSL certfile')
    p.add_argument('-K', '--SSLkey', type=str, help='Path to SSL keyfile')
    args = p.parse_args()
    LOG_FILE = args.logfile
    logger = Logger(port=args.port, cert=args.SSLcert, key=args.SSLkey)
    logger.run()
