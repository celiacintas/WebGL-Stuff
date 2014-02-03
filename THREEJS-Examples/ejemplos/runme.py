#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
import sys
import zmq.green as zmq
import time
import math
import json
# Debugger
from werkzeug.serving import run_with_reloader


gevent.monkey.patch_all()


from flask import Flask, request, Response, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@run_with_reloader
def main():
    '''Función mainl del programa'''

    host, port = '0.0.0.0', 8888
    print "Running server at {host}:{port}".format(host=host, port=port)

    #gevent.spawn(retransmisor)
    #gevent.spawn(sender)
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()


if __name__ == '__main__':
    sys.exit(main())
