# -*- coding: utf-8 -*-

# all the imports

import os
import os.path
import datetime
import time
import arrow
import requests
from requests.exceptions import ConnectionError


from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import secure_filename


# app instance
app = Flask(__name__)

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
DATABASE = os.path.join(app.root_path, 'db/irrigation.db')
IRRIGATION_ENDPOINT = "http://192.168.1.11/irrigate"

app.config.from_object(__name__)


# controllers
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/irrigate", methods=['POST'])
def irrigate():
    seconds = request.form['seconds']
    if seconds.isdigit():
        irrigate_plant(int(seconds))
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
        print "Error de conexión"


def send_command(seconds):
    print 'send_command', seconds
    irrigation_params = {'seconds': seconds}
    r = requests.get(IRRIGATION_ENDPOINT, params=irrigation_params)
    if r.status_code != 200:
        raise ConnectionError


def log(seconds):
    # TODO: log in DB
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0')
