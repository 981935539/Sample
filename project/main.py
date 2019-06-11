# coding=utf-8

import sys
import logging
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.web
from tornado.options import define, options
from apscheduler.schedulers.tornado import TornadoScheduler

import settings
from ai import outpatient_service, airesult_service, uploadimage_service, query_uploadinfo
from db import db_session, dbengine, init_db
from urls import HADNLERS
from workers import study_upload, report_upload, query_studyuids


class Application(tornado.web.Application):
    def __init__(self):
        self.init_logger()
        logging.info(u'init Application...')

        app_settings = dict(
            debug=settings.get('DEBUG', False),
            compress_response=True,
        )

        tornado.web.Application.__init__(self, HADNLERS, **app_settings)
        dbengine.dispose()
        init_db()
        self.db = db_session

    def init_logger(self):
        log_dir = settings.get("LOGCONF").get("dir", "./log")
        log_name = '{0}.log'.format(settings.get("LOGCONF").get("name", "main"))
        os.makedirs(log_dir, exist_ok=True)

        from logging.handlers import RotatingFileHandler
        logfile = RotatingFileHandler(os.path.join(log_dir, 'main.log'), maxBytes=1024*1024*50, backupCount=int(settings.get("LOGCONF").get("count", "10")))

        formatter = logging.Formatter('[%(asctime)s %(process)d %(module)s:%(funcName)s:%(lineno)d %(levelname)5s] %(message)s', '%Y%m%d %H:%M:%S')
        logfile.setFormatter(formatter)
        logging.getLogger('').setLevel(settings.get("LOGCONF").get("level", "DEBUG"))
        logging.getLogger('').addHandler(logfile)


def start_app():
    try:
        tornado.options.parse_command_line()
        app = Application()
        http_server = tornado.httpserver.HTTPServer(app, xheaders=True, max_buffer_size=1000*1024*1024)
        # http_server.listen(int(settings.get("PORT", "8085")))
        logging.info(u'starting service... ')

        scheduler = TornadoScheduler()
        # scheduler.add_job(ai_server, 'interval', seconds=3)
        if settings.IF_INCREASE_REPORT:
            scheduler.add_job(report_upload, 'cron', hour=4)
        if settings.IF_INCREASE_STUDY:
            scheduler.add_job(study_upload, 'cron', hour=4)
        scheduler.start()

        if settings.IF_AISERVER:
            tornado.ioloop.PeriodicCallback(query_uploadinfo, 2*60*1000).start()
            tornado.ioloop.PeriodicCallback(outpatient_service, 1*60*1000).start()
            tornado.ioloop.PeriodicCallback(uploadimage_service, 3*60*1000).start()
            tornado.ioloop.PeriodicCallback(airesult_service, 3*6*1000).start()
        # tornado.ioloop.IOLoop.current().spawn_callback(uploadimage_service)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        logging.info(u'stoping service...')
        tornado.ioloop.IOLoop.instance().stop()
    except Exception as e:
        logging.exception(e)
        raise e


def stop_app():
    tornado.ioloop.IOLoop.instance().stop()


if __name__ == "__main__":
    try:
        start_app()
    except KeyboardInterrupt as e:
        stop_app()
    except Exception as e:
        logging.exception(e)
        stop_app()
        raise e
