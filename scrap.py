#!/usr/bin/env python3
import datetime
import time
from dateutil import parser
from garrent.tasks import (insert_ccass_stock_holding_and_snapshot,
                           insert_share_holding,
                           insert_stock,
                           insert_ccass_player,
                           insert_repurchases_report,
                           insert_short_sell,
                           insert_sse_hk_stock,
                           insert_hk_stock_change,
                           insert_stock_top_10,
                           insert_stock_connect,
                           insert_list_IPO
                           )
import logging

logging.basicConfig(filename='garrent.log',level=logging.INFO)

if __name__ == '__main__':
    logging.info('Start Running at {}'.format(str(datetime.datetime.now())))
    tstart = time.time()
    today = datetime.date.today()
    """
    top10date = datetime.date(2017,3,6)
    logging.info('Running insert_stock_top_10()')
    insert_stock_top_10(top10date)
    """
    logging.info('Running insert_list_IPO()')
    insert_list_IPO()
    #logging.info('Running insert_stock_connect()')
    #insert_stock_connect()
    #logging.info('Running insert_sse_hk_stock()')
    #insert_sse_hk_stock()
    #logging.info('Running insert_hk_stock_change()')

    #insert_hk_stock_change()
    #logging.info('Running insert_stock()')
    #insert_stock()
    #logging.info('insert_ccass_player()')
    #insert_ccass_player()
"""
    curdate = today - datetime.timedelta(days=1)
    #curdate = datetime.date(2017,2,16)
    logging.info('Start grabbing on {}'.format(curdate))
    stocklist = Stock.all()
    while(curdate < today):
        if curdate.isoweekday() not in [6,7]:
            logging.info('insert_repurchases_report()')
            insert_repurchases_report(curdate)
            logging.info('insert_short_sell()')
            insert_short_sell(curdate)
            for s in stocklist:
                if(int(s.code) % 50 == 0): logging.info('grabbing {} on {}'.format(s.code,curdate))
                insert_ccass_stock_holding_and_snapshot(s.code,curdate)
                insert_share_holding(s.code,curdate,curdate)
        curdate = curdate + datetime.timedelta(days=1)
    duration = time.time() - tstart
    logging.info('Running time: {}'.format(duration))
"""
