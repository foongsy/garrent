#!/usr/bin/env python3

from redis import StrictRedis
from rq_scheduler import Scheduler
from datetime import datetime
import pytz

from garrent.jobs import update_stock

conn = StrictRedis(host='localhost',port=6379)
scheduler = Scheduler(connection=conn)

scheduler.schedule(
    scheduled_time=datetime(2017,3,17,3,20),
    func=update_stock,
    args=[True])
