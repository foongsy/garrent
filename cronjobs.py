#!/usr/bin/env python3

from redis import StrictRedis
from rq_scheduler import Scheduler
from datetime import datetime, timedelta
import pytz

from garrent.jobs import update_stock
from garrent.jobs import update_ccassplayer

conn = StrictRedis(host='localhost',port=6379)
scheduler = Scheduler(connection=conn)
scheduler.enqueue_at(datetime.utcnow(), update_stock)
scheduler.enqueue_at(datetime.utcnow(), update_ccassplayer)
"""
scheduler.schedule(
    scheduled_time=datetime.utcnow(), #+timedelta(minutes=1),
    func=update_stock,
    args=[True])
"""
"""
Crontab schedule for tasks
m h dom mon dow
0 7 * * 1-6 update_stock
0 4 * * 1-6 update_ccassplayer
5 4 * * 1-6 update_sbstock
10 4 * * 1-6 update_sbstock_change
0 2 * * 2-6 update_buyback
5 2 * * 2-6 update_shareholders
0 19 * * 1-5 update_shortsell
0 22 * * 1-5 update_ccass
0 1 * * 2-6 update_sbholdings
"""
