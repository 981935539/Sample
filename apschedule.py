# coding=utf-8

"""
Demonstrates how to use the Tornado compatible scheduler to schedule a job that executes on 3
second intervals.
"""

from datetime import datetime
import os

from tornado.ioloop import IOLoop, PeriodicCallback
from apscheduler.schedulers.tornado import TornadoScheduler


def tick():
    print('Tick! The time is: %s' % datetime.now())

def job():
	print('Every Day Job! The time is: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = TornadoScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    scheduler.add_job(job, 'cron', hour=10, minute=25)
    scheduler.start()
    PeriodicCallback(job, 2 * 1000).start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass