# coding=utf-8

from . import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.write("IndexHandler")