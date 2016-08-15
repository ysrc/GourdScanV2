#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.web

from settings import settings
from urls import url_patterns

from tornado.options import options
from base64 import decodestring as de64

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)
    @property
    def mail_connection(self):
        return ""


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port=options.port, address=options.address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
