
import os
import datetime
from dateutil import parser, rrule
from .database import pymysql_conn

# Loggly setting
import logging
import logging.config
import loggly.handlers

logging.config.fileConfig('logging.conf')
loggerr = logging.getLogger(__name__)
#

"""
# ELK setting
import logstash
logstash_host = 'elk.iamsophy.com'
loggerr = logging.getLogger("garrent-jobs")
elk.setLevel(logging.INFO)
elk.addHandler(logstash.LogstashHandler(logstash_host, 5959, version=1))
elk_extras = {
    'hostname':os.uname()[1]
    }
"""

def update_stock(cleanup=True):
    if cleanup:
        loggerr.info('update_stock with cleanup')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE stock;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    from .tasks import insert_stock
    loggerr.info('calls insert_stock')
    insert_stock()

def update_ccassplayer(cleanup=True):
    if cleanup:
        loggerr.info('update_ccassplayer with cleanup')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE ccass_player;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    from garrent.tasks import insert_ccass_player
    loggerr.info('calls with cleanup')
    insert_ccass_player()
