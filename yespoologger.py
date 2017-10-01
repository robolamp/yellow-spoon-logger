#! /usr/bin/env python3

import time
import os
import argparse
import ssl


from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

class Server(BaseHTTPRequestHandler):
    def _update_logfile(self, ts=time.time(), 
                              time=datetime.now().strftime("%d %b %Y %H:%M:%S.%f"),
                              whois="unknown:unknown",
                              data=''):
        
        self._logheader = "ts,datetime,user,data"
        self._logfilepath = ".post.log"
        
        if not os.path.exists(self._logfilepath):
            file = open(self._logfilepath, 'w+')
            file.write(self._logheader + "\n")
            file.close()

        logstring = '{},{},{},{}'.format(str(ts), time, whois, str(data))
        file = open(self._logfilepath, 'a')
        file.write(logstring + "\n")
        file.close()

    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        post_sender = ":".join([str(n) for n in self.client_address])
            
        self._update_logfile(
            whois = post_sender,
            data = post_data.decode('ascii')
        )

        self.send_response(200, message="OK")
        self.send_header('Content-type', 'text/html')
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
                                            certfile=self._path_to_key, 
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
    p = argparse.ArgumentParser(description='POST HTTP Requests logger')
    p.add_argument('-P', '--port', type=int, help='port')
    p.add_argument('-S', '--SSLcert', type=str, help='Path to SSL certfile')
    p.add_argument('-K', '--SSLkey', type=str, help='Path to SSL keyfile')
    args = p.parse_args()
    logger = Logger(port=args.port, cert=args.SSLcert, key=args.SSLkey)
    logger.run()
