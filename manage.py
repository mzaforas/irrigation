# -*- coding: utf-8 -*-
import arrow

from flask.ext.script import Manager

from irrigation import app, irrigate_plant, connect_db

manager = Manager(app)


@manager.option('-n', '--name', help='Node name')
@manager.option('-s', '--seconds', help='Irrigation seconds', default=1)
def irrigate(name, seconds):
    """Irrigate N seconds """
    irrigate_plant(name, int(seconds))


@manager.command
def periodic():
    """Trigger periodic irrigation if needed"""
    db_conn = connect_db(app)
    cursor = db_conn.cursor()
    nodes = cursor.execute('select id, name, frequency, seconds from nodes').fetchall()
    for node in nodes:
        name = node[1]
        frequency = node[2]
        seconds = node[3]

        period = 24/frequency

        if arrow.now().hour % period == 0:
            app.logger.info('[{}] {} periodic irrigation'.format(arrow.now().format('YYYY-MM-DD HH:mm'), name))
            irrigate_plant(name, int(seconds))

if __name__ == "__main__":
    manager.run()
