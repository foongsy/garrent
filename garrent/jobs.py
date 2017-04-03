
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

def update_sbstock(cleanup=True):
    if cleanup:
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE sb_stock;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    from garrent.tasks import insert_sz_hk_stock
    from garrent.tasks import insert_sse_hk_stock
    insert_sse_hk_stock()
    insert_sz_hk_stock()

def update_buyback(cleanup=False, today=False):
    if cleanup:
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE repurchase;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    if isinstance(today, datetime.datetime):
        from garrent.tasks import insert_repurchases_report
        insert_repurchases_report(today)

def update_shareholders(cleanup=False, today=False):
    if cleanup:
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE shareholders;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    if isinstance(today, datetime.datetime):
        from garrent.tasks import insert_share_holding
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.active == True)
        for s in stocks:
            insert_share_holding(s.code, today, today)

def update_shortsell(cleanup=False, today=False):
    if cleanup:
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE shortsell;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    if isinstance(today, datetime.datetime):
        from garrent.tasks import insert_short_sell
        insert_short_sell(today)

def update_ccass(cleanup=False, today=False):
    if cleanup:
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE ccass_snapshot;'
                cursor.execute(sql)
                sql = 'TRUNCATE ccass_details;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    if isinstance(today, datetime.datetime):
        from garrent.tasks import insert_ccass_stock_holding_and_snapshot
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.active == True)
        for s in stocks:
            insert_ccass_stock_holding_and_snapshot(s.code, today)


"""
def update_sbstock_change(cleanup=True):
    if cleanup:
        loggerr.info('update_ccassplayer with cleanup')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE sb_stockchange;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
"""
