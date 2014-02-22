# -*- coding: utf-8 -*-

# all the imports

import logging
import socket
import os
import os.path
import arrow
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

STATUS_OK = 1
STATUS_ERROR = 0

file_handler = logging.FileHandler(os.path.join(app.root_path, 'log/irrigation.log'))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

app.logger.addHandler(file_handler)

app.config.from_object(__name__)


# controllers
@app.route("/")
def index():
    db_conn = getattr(g, 'db_conn', None)
    cursor = db_conn.cursor()

    logs = cursor.execute('select datetime(timestamp, "unixepoch", "localtime"), status, irrigation_seconds, node_id from logs order by timestamp desc limit 10').fetchall()

    nodes = cursor.execute('select id, name, frequency, seconds from nodes').fetchall()

    return render_template('index.html', logs=logs, nodes=nodes)


@app.route("/irrigate", methods=['POST'])
def irrigate():
    seconds = request.form['seconds']
    name = request.form['name']

    if seconds.isdigit():
        try:
            irrigate_plant(name, int(seconds))
        except ConnectionError:
            flash(u'Error de conexión enviando orden de riego a {}'.format(name), category='danger')
        else:
            flash(u'Enviada orden de riego a {} durante {} segundos'.format(name, seconds), category='success')
    else:
        flash(u'Número de segundos de riego debe ser un entero', category='danger')
    return redirect(url_for('index'))


# aux functions
def irrigate_plant(node_name, seconds):
    try:
        send_command(node_name, seconds)
        log(seconds, status=STATUS_OK)
    except ConnectionError:
        app.logger.error('[{}] Connection error'.format(arrow.now().format('YYYY-MM-DD HH:mm')))
        log(seconds, status=STATUS_ERROR)
        raise
    

def send_command(host, seconds):
    app.logger.info('send_command %s %d', host, seconds)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))
        s.sendall(chr(seconds))
        s.close()
    except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        raise ConnectionError

    # HTTP version not used
    # irrigation_params = {'seconds': seconds}
    # r = requests.get(IRRIGATION_ENDPOINT, params=irrigation_params)
    # if r.status_code != 200:
    #     raise ConnectionError


def log(seconds, status):
    now = arrow.now()

    app.logger.info('[{}] Write log in DB'.format(now.format('YYYY-MM-DD HH:mm')))

    db_conn = getattr(g, 'db_conn', None)
    if db_conn is None:
        db_conn = connect_db(app)

    cursor = db_conn.cursor()
    cursor.execute('insert into logs (timestamp, status, irrigation_seconds, node_id) values (?, ?, ?, ?)',
                   (now.timestamp, status, seconds, 1))
    db_conn.commit()
 
    if db_conn is not None:
        db_conn.close()


@app.route("/update-node", methods=['POST'])
def update_node():
    node_id = request.form['id']
    frequency = request.form['frequency']
    seconds = request.form['seconds']

    db_conn = getattr(g, 'db_conn', None)
    cursor = db_conn.cursor()
    cursor.execute('update nodes set frequency=?, seconds=? where id=?',
                   (frequency, seconds, node_id))
    db_conn.commit()

    flash(u'Parámetros de riego actualizados a <b>{}</b> veces al día durante <b>{}</b> segundos'
          .format(frequency, seconds), category='success')
    return redirect(url_for('index'))


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
