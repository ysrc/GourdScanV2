#!/usr/bin/env python
# -*- coding: utf-8 -*-
import handlers.main
import tornado.web

url_patterns =  [
    (r"^/", tornado.web.RedirectHandler,
     dict(url="/urls.scan")),
    (r"^/raw/([^/]+)?", handlers.main.ShowRawHttpHandler),
    (r"^/urls.scan?", handlers.main.ShowUrlsHandler),
    (r"^/sqli.scan", handlers.main.ShowSqliHandler),
    (r"^/xss.scan", handlers.main.ShowXssHandler),
    (r"^/xpath.scan", handlers.main.ShowXpathHandler),
    (r"^/ldap.scan", handlers.main.ShowLdapHandler),
    (r"^/lfi.scan", handlers.main.ShowLfiHandler),
    (r"^/sqli_time.scan", handlers.main.ShowSqliTimeHandler),
    (r"^/configuration.scan", handlers.main.ConfHandler),
]

