# -*- coding: utf-8 -*-

# all the imports

import socket
import struct
import os
import os.path
import arrow
import requests
from requests.exceptions import ConnectionError

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# app instance
app = Flask(__name__)

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
DATABASE = os.path.join(app.root_path, 'db/irrigation.db')
IRRIGATION_ENDPOINT = "http://pump/irrigate"

app.config.from_object(__name__)


# controllers
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/irrigate", methods=['POST'])
def irrigate():
    seconds = request.form['seconds']
    if seconds.isdigit():
        try:
            irrigate_plant(int(seconds))
        except ConnectionError:
            flash(u'Error de conexión enviando orden de riego', category='danger')
        else:
            flash(u'Enviada orden de riego durante {seconds} segundos'.format(seconds=seconds), category='success')
    else:
        flash(u'Número de segundos de riego debe ser un entero', category='danger')
    return redirect(url_for('index'))


# aux functions
def irrigate_plant(seconds):
    try:
        send_command(seconds)
        log(seconds)
    except ConnectionError:
        app.logger.error('Error de conexión %s' % arrow.now().format('YYYY-MM-DD HH:mm'))
        raise
    


def send_command(seconds):
    app.logger.info('send_command %d', seconds)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('pump', 80))
    s.sendall(chr(seconds))
    # irrigation_params = {'seconds': seconds}
    # r = requests.get(IRRIGATION_ENDPOINT, params=irrigation_params)
    # if r.status_code != 200:
    #     raise ConnectionError


def log(seconds):
    # TODO: log in DB
    app.logger.info(arrow.now().format('YYYY-MM-DD HH:mm'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
