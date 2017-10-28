# yellow-spoon-logger
Just a very simple server which is recording HTTP (and HTTPS) POST requests to .log file

# How to run

yespoologger.py [-P PORT] [-L path-to-logfile] [-S path-to-SSLCERT] [-K path-to-SSLKEY]

If SSLcert and SSLKey aren't provided, it will work as HTTP server.

# How to stop

Just Ctrl+C

The logfile will be at ./.post.log
