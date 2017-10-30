#! /usr/bin/env python3

import time
import os
import argparse
import ssl


from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

LOG_FILE = ".post.log"

class Server(BaseHTTPRequestHandler):
    def _update_logfile(self, type="POST",
                              ts=0.0,
                              time="unknown",
                              whois="unknown:unknown",
                              data=""):

        self._logheader = "type,ts,datetime,user,data"
        self._logfilepath = LOG_FILE

        if not os.path.exists(self._logfilepath):
            file = open(self._logfilepath, 'w+')
            file.write(self._logheader + "\n")
            file.close()

        logstring = '{},{},{},{},{}'.format(type,
                                            str(ts),
                                            time,
                                            whois,
                                            str(data))
        file = open(self._logfilepath, 'a')
        file.write(logstring + "\n")
        file.close()


    def _log_request(self, req_type):
        req_data = self.rfile.read(int(self.headers['Content-Length']))
        req_sender = ":".join([str(n) for n in self.client_address])

        self._update_logfile(
            type = req_type,
            ts=time.time(),
            time=datetime.now().strftime("%d %b %Y %H:%M:%S.%f"),
            whois = req_sender,
            data = req_data.decode('ascii')
        )

    def do_POST(self):
        self._log_request("POST")

        self.send_response(200, message="OK")
        self.end_headers()

    def do_GET(self):
        self._log_request("GET")

        self.send_response(200)
        self.end_headers()

class Logger(object):
    def __init__(self, port=9090, cert=None, key=None):
        self._port = port
        self._path_to_cert = cert
        self._path_to_key = key

    def run(self):
        server_address = ('', self._port)
        server = HTTPServer(server_address, Server)

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
    p = argparse.ArgumentParser(description='GET and POST HTTP Requests logger')
    p.add_argument('-P', '--port', type=int, help='port')
    p.add_argument('-L', '--logfile', type=str, default=".post.log", help='Path to logfile')
    p.add_argument('-S', '--SSLcert', type=str, help='Path to SSL certfile')
    p.add_argument('-K', '--SSLkey', type=str, help='Path to SSL keyfile')
    args = p.parse_args()
    LOG_FILE = args.logfile
    logger = Logger(port=args.port, cert=args.SSLcert, key=args.SSLkey)
    logger.run()
