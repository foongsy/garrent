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
