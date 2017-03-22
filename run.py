#!/usr/bin/env python3
import click
import datetime
from dateutil import parser, rrule
from garrent.database import pymysql_conn
from datetime import timedelta

# Loggly setting
import logging
import logging.config
import loggly.handlers

logging.config.fileConfig('logging.conf')
loggerr = logging.getLogger(__name__)
#

from rq import Queue
from redis import StrictRedis
from rq import get_failed_queue, push_connection

today = datetime.date.today()

redis_conn = StrictRedis()
queue = Queue(connection=redis_conn)
ccass_q = Queue('ccass',connection=redis_conn)
buyback_q = Queue('buyback',connection=redis_conn)
shareholder_q = Queue('shareholder',connection=redis_conn)

from garrent.jobs import update_stock, update_ccassplayer

@click.group()
def run():
    pass

@run.command()
def initdb():
    from garrent import models, database
    models.Base.metadata.bind = database.engine
    models.Base.metadata.create_all(database.engine)
    click.echo("Database inited")

@run.command()
def status():
    from garrent.pw_models import Stock
    mainboard = Stock.select().where(Stock.board == 'M')
    gemboard = Stock.select().where(Stock.board == 'G')
    click.echo(" - There are {} main board stocks".format(len(mainboard)))
    click.echo(" - There are {} GEM stocks".format(len(gemboard)))

@run.command()
@click.option('--cleanup', is_flag=True, help='Empty the list before updating')
def stock(cleanup):
    return update_stock(cleanup=cleanup)

@run.command()
@click.option('--cleanup', is_flag=True, help='Empty the list before updating')
def ccassplayer(cleanup):
    return update_ccassplayer(cleanup=cleanup)

@run.command()
@click.option('--daysback', nargs=1, type=int, help="Update buyback from N days before specific date, inclusively")
@click.argument('date', type=str) #, help="Update buyback for the date, (YYYY-MM-DD)")
def buyback(date,daysback):
    if date:
        p_date = parser.parse(date)
        from garrent.tasks import insert_repurchases_report
        click.echo('- Date specified {}...'.format(date))
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
            click.echo('- Start from {} days back: {}'.format(daysback, datetime.date.strftime(start_date, "%Y-%m-%d")))
            for cur_date in rrule.rrule(freq=rrule.DAILY,dtstart=start_date,until=p_date):
                if cur_date.weekday() < 5:
                    insert_repurchases_report(cur_date)
            click.echo('- Done')
        else:
            insert_repurchases_report(p_date)
            click.echo('- Done')
"""
    if period:
        click.echo('  Updating buyback for {} to {}'.format(*period))
"""
"""
@run.command()
@click.option('--daysback', nargs=1, type=int, help="Update shareholding from N days before specific date, inclusively")
@click.argument('date', type=str)
def shareholder(date,daysback):
    if date:
        p_date = parser.parse(date)
        from garrent.tasks import insert_share_holding
        click.echo('- Date specified {}...'.format(date))
        from garrent.pw_models import Stock
        stocks = Stock.select()
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
        else:
            start_date = p_date
        click.echo('- Start from {} till {}'.format(datetime.date.strftime(start_date, "%Y-%m-%d"),datetime.date.strftime(p_date, "%Y-%m-%d")))
        for s in stocks:
            insert_share_holding(s.code, start_date, p_date)
        click.echo('- Done')
"""

@run.command()
@click.argument('start_date', type=str)
@click.argument('end_date', type=str)
def q_shareholder(start_date,end_date):
    if start_date and end_date:
        loggerr.info('[q_shareholder] date: {}-{}'.format(start_date, end_date))
        p_start_date = parser.parse(start_date)
        p_end_date = parser.parse(end_date)
        from garrent.tasks import insert_share_holding
        click.echo('- Date specified {}-{}'.format(p_start_date, p_end_date))
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.active == True)
        loggerr.info('[q_shareholder] number of stocks to be process: {}'.format(len(stocks)))
        for s in stocks:
            loggerr.info('[q_shareholder] code={}, start_date={}, p_date={}'.format(s.code, p_start_date, p_end_date))
            shareholder_q.enqueue(insert_share_holding, s.code, p_start_date, p_end_date)

@run.command()
@click.argument('start_date', type=str)
@click.argument('end_date', type=str)
def q_ccass(start_date,end_date):
    if start_date and end_date:
        loggerr.info('[q_ccass] date: {}-{}'.format(start_date,end_date))
        p_start_date = parser.parse(start_date)
        p_end_date = parser.parse(end_date)
        click.echo('- Date specified {}-{}'.format(p_start_date,p_end_date))
        from garrent.tasks import insert_ccass_stock_holding_and_snapshot
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.active == True)
        loggerr.info('[q_ccass] number of stocks to be process: {}'.format(len(stocks)))
        cur_date = p_start_date
        while cur_date <= p_end_date:
            if cur_date.weekday() < 5:
                for s in stocks:
                    loggerr.info('[q_ccass] working on: {}, {}'.format(s.code,cur_date.date()))
                    ccass_q.enqueue(insert_ccass_stock_holding_and_snapshot, s.code, cur_date)
            cur_date += timedelta(days=1)

"""
@run.command()
@click.argument('date', type=str)
def ccass(date):
    if date:
        loggerr.info('[ccass] date: {}'.format(date))
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.tasks import insert_ccass_stock_holding_and_snapshot
        from garrent.pw_models import Stock
        stocks = Stock.select()
        loggerr.info('[ccass] number of stocks to be process: {}'.format(len(stocks)))
        for s in stocks:
            loggerr.info('[ccass] working on: {}, {}'.format(s.code,p_date.date))
            insert_ccass_stock_holding_and_snapshot(s.code,p_date)
"""

@run.command()
@click.argument('start_date', type=str)
@click.argument('end_date', type=str)
def sbtop10(start_date, end_date):
    if start_date and end_date:
        loggerr.info('[sbtop10] date: {}-{}'.format(start_date,end_date))
        p_start_date = parser.parse(start_date)
        p_end_date = parser.parse(end_date)
        click.echo('- Date specified {}-{}'.format(p_start_date,p_end_date))
        from garrent.tasks import insert_stock_top_10
        for cur_date in rrule.rrule(freq=rrule.DAILY, dtstart=p_start_date, until=p_end_date):
            insert_stock_top_10(cur_date)

@run.command()
@click.argument('date', type=str)
def shortsell(date):
    if date:
        loggerr.info('[shortsell] date: {}'.format(date))
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.tasks import insert_short_sell
        insert_short_sell(date)

@run.command()
def ipo():
    #from garrent.tasks import insert_list_IPO
    #insert_list_IPO()
    from garrent.tasks import inster_stock_IPO_info
    from garrent.pw_models import StockIpo
    stocks = StockIpo.select(StockIpo.code).where(StockIpo.company_name.is_null())
    for s in stocks:
        inster_stock_IPO_info(s.code)
        loggerr.info('[ipo_info] : {}'.format(s.code))

@run.command()
def sbstock():
    from garrent.tasks import insert_sz_hk_stock
    from garrent.tasks import insert_sse_hk_stock
    insert_sse_hk_stock()
    insert_sz_hk_stock()

@run.command()
def failed():
    push_connection(redis_conn)
    failed = get_failed_queue()
    for j in failed.jobs:
        print(j)

@run.command()
@click.argument('date', type=str)
def sbholding(date):
    from garrent.tasks import insert_sbholding
    insert_sbholding(date)

#insert_hk_stock_change
#insert_stock_connect
#insert_list_IPO
#inster_stock_IPO_info


if __name__ == '__main__':
    run()

"""

"""
