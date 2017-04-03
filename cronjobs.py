#!/usr/bin/env python3

from redis import StrictRedis
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
import pytz

from garrent.jobs import update_stock
from garrent.jobs import update_ccassplayer
from garrent.jobs import update_sbstock
from garrent.jobs import update_buyback
from garrent.jobs import update_shareholders
from garrent.jobs import update_shortsell


def hkt_to_utc(t):
    if not isinstance(t, datetime.datetime):
        return(False)
    local = pytz.timezone("Asia/Hong_Kong")
    local_dt = local.localize(t, is_dst=None)
    return(local_dt.astimezone(pytz.utc))


conn = StrictRedis(host='localhost',port=6379)
scheduler = Scheduler(connection=conn)

hk_yday = datetime.now() - timedelta(days=1)
hk_today = datetime.now()

# Update all stock list at local time '0 7 * * 1-6'
scheduler.cron(
    '0 23 * * 0-5',
    func=update_stock,
    args=[],
    kwargs={},
    repeat=None,
    queue_name='stock')

# Update ccass player list at local time '0 4 * * 1-6'
scheduler.cron(
    '0 20 * * 0-5',
    func=update_ccassplayer,
    args=[],
    kwargs={},
    repeat=None,
    queue_name='ccass_player')

# Update sbstock list at local time '5 4 * * 1-6'
scheduler.cron(
    '5 20 * * 0-5',
    func=update_sbstock,
    args=[],
    kwargs={},
    repeat=None,
    queue_name='sbstock')

"""
# Update sbstock change at local time '10 4 * * 1-6'
scheduler.cron(
    '10 20 * * 0-5',
    func=update_sbstock_change,
    args=[],
    kwargs={},
    repeat=None,
    queue_name='sbstock')
"""

# Update update_buyback at local time '0 2 * * 2-6'
scheduler.cron(
    '0 18 * * 1-5',
    func=update_buyback,
    args=[],
    kwargs={'today': hk_yday},
    repeat=None,
    queue_name='buyback')

# Update update_shareholders at local time '5 2 * * 2-6'
scheduler.cron(
    '5 18 * * 1-5',
    func=update_shareholders,
    args=[],
    kwargs={'today': hk_yday},
    repeat=None,
    queue_name='shareholders')

# Update update_shortsell at local time '30 22 * * 1-5'
scheduler.cron(
    '30 14 * * 1-5',
    func=update_shortsell,
    args=[],
    kwargs={'today': hk_today},
    repeat=None,
    queue_name='shortsell')

# Update update_ccass at local time '30 0 * * 2-6'
"""
scheduler.cron(
    '30 16 * * 1-5',
    func=update_ccass,
    args=[],
    kwargs={'today', hk_yday},
    repeat=None,
    queue_name='ccass')
"""
"""
Crontab schedule for tasks
m h dom mon dow
'0 1 * * 2-6' update_sbholdings
"""
