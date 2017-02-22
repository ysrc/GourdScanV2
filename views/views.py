#!/usr/bin/env python
#coding: utf-8

import os
import site #Add the boilerplate's directories to Python's site-packages path.
import tornado.web
import tornado.ioloop
from lib import lib_out
from lib import lib_config
from urls import url_patterns
from lib import lib_config as config
from tornado.options import define, options 

def make_app(settings):
    return tornado.web.Application(url_patterns, **settings)

def main():
    define("port", default=int(lib_config.load()["port"]), type=int)
    define("address", default=lib_config.load()["ip"])
    tornado.options.parse_command_line()
    path = lambda root,*a: os.path.join(root, *a)
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
    config.update(conf)
    app = make_app(settings)
    app.listen(port=options.port, address=options.address)
    lib_out.good("Web app start at: http://%s:%s" % (options.address, options.port))
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
