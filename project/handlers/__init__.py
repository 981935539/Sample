import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def on_finish(self):
        self.db.remove()


from .index import IndexHandler