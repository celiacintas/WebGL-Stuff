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
#
from multiprocessing import Process

gevent.monkey.patch_all()


from flask import Flask, request, Response, render_template


app = Flask(__name__)
app.context = zmq.Context()

DIRECCION_PUBLICADOR = 'tcp://127.0.0.1:5555'

def kinect_simulator(qapp_args=None):
    from PyQt4.QtGui import (
                             QApplication,
                             QWidget, QSpinBox, QHBoxLayout,
                             QSlider, QPushButton)
    import json
    import zmq
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)
    socket.bind(DIRECCION_PUBLICADOR)

    slider1, slider2 = None, None
    if not qapp_args:
        qapp_args = []
    def value_changed(value):
        data = {'mouseX': int(slider1.value()), 'mouseY': int(slider2.value())}
        message = json.dumps(data)
        socket.send(message)

    app = QApplication(qapp_args)
    win = QWidget()
    win.setWindowTitle("Send events to kinect")
    layout = QHBoxLayout()
    slider1 = QSlider()
    slider1.setMinimum(100)
    slider1.setMaximum(600)
    layout.addWidget(slider1)
    slider2 = QSlider()
    slider2.setMinimum(100)
    slider2.setMaximum(600)
    layout.addWidget(slider2)
    slider1.valueChanged[int].connect(value_changed)
    slider2.valueChanged[int].connect(value_changed)
    win.setLayout(layout)
    win.show()

    return app.exec_()

def generador_de_eventos():
    '''Una función que envía acutalizaciones usando el protocolo de
    eventos emitidos por el servidor (SSE). La directiva yield retorna
    un valor, pero la función conserva su estado ante cada llamada, por
    eso está rodeada de un while True'''
    sock = app.context.socket(zmq.SUB)
    sock.connect(DIRECCION_PUBLICADOR)
    sock.setsockopt(zmq.SUBSCRIBE, "")
    while True:
        data = sock.recv()
        print "Sending %s to client" % data
        # Yield retorna un valor pero guarda estado de una función
        yield 'data: %s\n\n' % data


@app.route('/events')
def sse_request():
    '''URL donde se publican los eventos'''
    return Response(generador_de_eventos(), mimetype='text/event-stream')

@app.route('/')
def index():
    return render_template('index.html')

@run_with_reloader
def main():
    '''Función mainl del programa'''
    p = Process(target=kinect_simulator)
    p.start()
    host, port = '0.0.0.0', 8888
    print "Running server at {host}:{port}".format(host=host, port=port)

    #gevent.spawn(retransmisor)
    #gevent.spawn(sender)
    http_server = WSGIServer((host, port), app)
    http_server.serve_forever()
    p.kill()

if __name__ == '__main__':
    sys.exit(main())
