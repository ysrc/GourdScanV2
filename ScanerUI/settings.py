#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import tornado
import tornado.template
import os
from tornado.options import define, options # lou xi. chen left

import environment
import logconfig

path = lambda root,*a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

define("port", default=7777, help="run on the given port", type=int)
define("address", default="127.0.0.1", help="address, understand?")
define("proxy", default="", help="http proxy", type=str)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")
tornado.options.parse_command_line()

MEDIA_ROOT = path(ROOT, 'media')
TEMPLATE_ROOT = path(ROOT, 'templates')
DATABASE = path(ROOT, 'dataBase.sqlite3')

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4
    }

if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO

settings = {}
settings['debug'] = options.debug #DEPLOYMENT != DeploymentType.PRODUCTION or
settings['static_path'] = MEDIA_ROOT
settings['cookie_secret'] = "O3h80XXsQiyTiH1eNgKBzQnJrgVuieykhk/yqh0/BTw="
settings['xsrf_cookies'] = False
settings['template_loader'] = tornado.template.Loader(TEMPLATE_ROOT)

SYSLOG_TAG = "boilerplate"
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL2

# See PEP 391 and logconfig for formatting help.  Each section of LOGGERS
# will get merged into the corresponding section of log_settings.py.
# Handlers and log levels are set up automatically based on LOG_LEVEL and DEBUG
# unless you set them here.  Messages will not propagate through a logger
# unless propagate: True is set.
LOGGERS = {
   'loggers': {
        'boilerplate': {},
    },
}

if settings['debug']:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = DEPLOYMENT != DeploymentType.SOLO

#logconfig.initialize_logging(SYSLOG_TAG, SYSLOG_FACILITY, LOGGERS,
#        LOG_LEVEL, USE_SYSLOG)

if options.config:
    tornado.options.parse_config_file(options.config)
