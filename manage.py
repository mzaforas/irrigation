# -*- coding: utf-8 -*-
import requests
import arrow

from flask.ext.script import Manager

from irrigation import app, irrigate_plant

manager = Manager(app)


@manager.option('-s', '--seconds', help='Irrigation seconds', default=1)
def irrigate(seconds):
    """Irrigate N seconds """
    irrigate_plant(int(seconds))


if __name__ == "__main__":
    manager.run()
