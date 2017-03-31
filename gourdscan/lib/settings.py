# coding: utf-8

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECK_CONF_FILE = os.path.join(ROOT, 'conf/', 'conf.json')

RULES_PATH = os.path.join(ROOT, 'conf/', 'rules/')

RULES_CONF_FILE = os.path.join(RULES_PATH, 'rule.conf')

SESSION_CONF_FILE = os.path.join(ROOT, 'conf/', 'session')

CONF_PATH = os.path.join(ROOT, 'conf/')