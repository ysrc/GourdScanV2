#!/usr/bin/env python
# coding: utf-8

import os
import site  # Add the boilerplate's directories to Python's site-packages path.

import tornado.web
import tornado.ioloop

from tornado.options import define, options

from gourdscan.lib import out
from gourdscan.lib import config
from gourdscan.web.urls import url_patterns


def make_app(settings):
    return tornado.web.Application(url_patterns, **settings)


def main():
    define("port", default=int(config.load()["port"]), type=int)
    define("address", default=config.load()["ip"])
    tornado.options.parse_command_line()
    path = lambda root, *a: os.path.join(root, *a)
    ROOT = os.path.dirname(os.path.abspath(__file__))
    settings = {}
    settings['static_path'] = path(ROOT, "static")
    settings['template_loader'] = tornado.template.Loader(path(ROOT, "templates"))
    settings['login_url'] = "/login"
    site.addsitedir(path(ROOT, 'handlers'))
    conf = config.load()
    conf['scapy_stat'] = 'false'
    conf['tornado_stat'] = 'false'
    conf['scan_stat'] = 'false'
    conf['mix_stat'] = 'false'
    conf['tornado_run_stat'] = 'false'
    config.update(conf)
    app = make_app(settings)
    app.listen(port=options.port, address=options.address)
    out.good("Web app start at: http://%s:%s" % (options.address, options.port))
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
