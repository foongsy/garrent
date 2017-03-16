#!/usr/bin/env python3
import click
import datetime
from dateutil import parser, rrule
from garrent.database import pymysql_conn
import logging
logging.basicConfig(level=logging.INFO)

from rq import Queue
from redis import StrictRedis
from rq import get_failed_queue, push_connection

today = datetime.date.today()

redis_conn = StrictRedis()
queue = Queue(connection=redis_conn)
ccass_q = Queue('ccass',connection=redis_conn)
buyback_q = Queue('buyback',connection=redis_conn)
shareholder_q = Queue('shareholder',connection=redis_conn)

from garrent.jobs import update_stock

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
    return update_stock(cleanup)

@run.command()
@click.option('--cleanup', is_flag=True, help='Empty the list before updating')
def ccassplayer(cleanup):
    if cleanup:
        click.echo('Cleanup existing CCASS player list')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE ccass_player;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    click.echo('Updating CCASS player')
    from garrent.tasks import insert_ccass_player
    insert_ccass_player()

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

@run.command()
@click.option('--daysback', nargs=1, type=int, help="Update shareholding from N days before specific date, inclusively")
@click.argument('date', type=str)
def shareholder(date,daysback):
    if date:
        p_date = parser.parse(date)
        from garrent.tasks import insert_share_holding
        click.echo('- Date specified {}...'.format(date))
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.board == 'M')
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
        else:
            start_date = p_date
        click.echo('- Start from {} till {}'.format(datetime.date.strftime(start_date, "%Y-%m-%d"),datetime.date.strftime(p_date, "%Y-%m-%d")))
        for s in stocks:
            insert_share_holding(s.code, start_date, p_date)
        click.echo('- Done')

@run.command()
@click.option('--daysback', nargs=1, type=int, help="Update shareholding from N days before specific date, inclusively")
@click.argument('date', type=str)
def q_shareholder(date,daysback):
    if date:
        p_date = parser.parse(date)
        from garrent.tasks import insert_share_holding
        click.echo('- Date specified {}...'.format(date))
        from garrent.pw_models import Stock
        stocks = Stock.select().where(Stock.board == 'M')
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
        else:
            start_date = p_date
        click.echo('- Start from {} till {}'.format(datetime.date.strftime(start_date, "%Y-%m-%d"),datetime.date.strftime(p_date, "%Y-%m-%d")))
        for s in stocks:
            shareholder_q.enqueue(insert_share_holding,s.code, start_date, p_date)
        click.echo('- Done')

@run.command()
@click.argument('date', type=str)
def q_ccass(date):
    if date:
        logging.debug('[ccass] date: {}'.format(date))
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.tasks import insert_ccass_stock_holding_and_snapshot
        from garrent.pw_models import Stock
        stocks = Stock.select().limit(100)
        logging.debug('[ccass] number of stocks to be process: {}'.format(len(stocks)))
        for s in stocks:
            logging.debug('[ccass] working on: {}, {}'.format(s.code,p_date.date))
            ccass_q.enqueue(insert_ccass_stock_holding_and_snapshot, s.code, p_date)

@run.command()
@click.argument('date', type=str)
def ccass(date):
    if date:
        logging.debug('[ccass] date: {}'.format(date))
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.tasks import insert_ccass_stock_holding_and_snapshot
        from garrent.pw_models import Stock
        stocks = Stock.select()
        logging.debug('[ccass] number of stocks to be process: {}'.format(len(stocks)))
        for s in stocks:
            logging.debug('[ccass] working on: {}, {}'.format(s.code,p_date.date))
            insert_ccass_stock_holding_and_snapshot(s.code,p_date)

@run.command()
@click.argument('date', type=str)
def sbtop10(date):
    if date:
        logging.debug('[sbtop10] date: {}'.format(date))
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.tasks import insert_stock_top_10
        insert_stock_top_10(p_date)

@run.command()
@click.argument('date', type=str)
def shortsell(date):
    if date:
        logging.debug('[shortsell] date: {}'.format(date))
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
        logging.debug('[ipo_info] : {}'.format(s.code))

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
    for j in failed:
        print(j)


#insert_hk_stock_change
#insert_stock_connect
#insert_list_IPO
#inster_stock_IPO_info


if __name__ == '__main__':
    run()

"""

"""
