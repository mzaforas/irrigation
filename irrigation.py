# -*- coding: utf-8 -*-

# all the imports

import os
import os.path
import datetime
import time
import arrow

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
app.config.from_object(__name__)

# controllers
@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
