#!/usr/bin/env python3
import click
import datetime
from dateutil import parser, rrule
from garrent.database import pymysql_conn

today = datetime.date.today()

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
def update_stock(cleanup):
    if cleanup:
        click.echo('Cleanup existing stock list')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE stock;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    click.echo('Updating Hong Kong stock list')
    from garrent.tasks import insert_stock
    insert_stock()

@run.command()
def update_ccassplayers():
    click.echo('Updating CCASS players')
    from garrent.tasks import insert_ccass_player
    #insert_ccass_player()

@run.command()
@click.option('--daysback', nargs=1, type=int, help="Update buyback from N days before specific date, inclusively")
@click.argument('date', type=str) #, help="Update buyback for the date, (YYYY-MM-DD)")
def update_buyback(date,daysback):
    if date:
        p_date = parser.parse(date)
        from garrent.tasks import insert_repurchases_report
        click.echo('- Date specified {}...'.format(date))
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
            click.echo('- Start from {} days back: {}'.format(daysback, datetime.date.strftime(start_date, "%Y-%m-%d")))
            for cur_date in rrule.rrule(freq=rrule.DAILY,dtstart=start_date,until=p_date):
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
def update_shareholder(date,daysback):
    if date:
        p_date = parser.parse(date)
        click.echo('- Date specified {}...'.format(date))
        from garrent.pw_models import Stock
        s = Stock.select()
        if daysback:
            start_date = p_date - datetime.timedelta(days=daysback)
            click.echo('- Start from {} till {}'.format(datetime.date.strftime(start_date, "%Y-%m-%d"),datetime.date.strftime(p_date, "%Y-%m-%d")))





if __name__ == '__main__':
    run()

"""

"""
