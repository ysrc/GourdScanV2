#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web

from lib import session


def authenticated(method):
    def wrapper(self, *args, **kwargs):
        if not self.login:
            self.set_header("Location", "/login")
            self.set_status(302)
            return
        else:
            return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(tornado.web.RequestHandler):

    """
    All the function need to login
    """

    def initialize(self):
        cookie = self.get_cookie("ysrc_token")
        if cookie == "" or not session.check(cookie):
            self.login = False
        else:
            self.login = True
