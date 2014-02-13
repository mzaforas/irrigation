# -*- coding: utf-8 -*-

# all the imports

import socket
import struct
import os
import os.path
import arrow
import requests
from requests.exceptions import ConnectionError
from contextlib import closing
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# app instance
app = Flask(__name__)

# configuration
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
DATABASE = os.path.join(app.root_path, 'db/irrigation.db')

IRRIGATION_ENDPOINT = "http://azalea/irrigate"

app.config.from_object(__name__)


# controllers
@app.route("/")
def index():
    db_conn = getattr(g, 'db_conn', None)
    cursor = db_conn.cursor()
    logs = cursor.execute('select timestamp, status, irrigation_seconds, node_id from logs').fetchall()

    return render_template('index.html', logs=logs)


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

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('azalea', 80))
        s.sendall(chr(seconds))
        s.close()
    except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        raise ConnectionError

    # HTTP version not used
    # irrigation_params = {'seconds': seconds}
    # r = requests.get(IRRIGATION_ENDPOINT, params=irrigation_params)
    # if r.status_code != 200:
    #     raise ConnectionError


def log(seconds):
    now = arrow.now()

    app.logger.info(now.format('YYYY-MM-DD HH:mm'))

    db_conn = getattr(g, 'db_conn', None)
    cursor = db_conn.cursor()
    cursor.execute('insert into logs (timestamp, status, irrigation_seconds, node_id) values (?, ?, ?, ?)', (now.timestamp, 1, seconds, 1))
    db_conn.commit()


@app.before_request
def before_request():
    g.db_conn = connect_db(app)


@app.teardown_request
def teardown_request(exception):
    db_conn = getattr(g, 'db_conn', None)
    if db_conn is not None:
        db_conn.close()

# DB auxiliar functions
def connect_db(app):
    return sqlite3.connect(app.config['DATABASE'])


def init_db(app):
    with closing(connect_db(app)) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
