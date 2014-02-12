#!/usr/bin/python
import sys
sys.path.insert(0, '/home/pi/irrigation/')

from flup.server.fcgi import WSGIServer
from irrigation import app

if __name__ == '__main__':
    WSGIServer(app).run()
