
import datetime
from dateutil import parser, rrule
from garrent.database import pymysql_conn
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

today = datetime.date.today()

def update_stock(cleanup):
    if cleanup:
        #click.echo('Cleanup existing stock list')
        try:
            conn = pymysql_conn()
            with conn.cursor() as cursor:
                sql = 'TRUNCATE stock;'
                cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()
    #click.echo('Updating Hong Kong stock list')
    from garrent.tasks import insert_stock
    insert_stock()
