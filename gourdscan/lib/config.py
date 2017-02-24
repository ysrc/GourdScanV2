# coding: utf-8

"""
Config and update/reload file
get test param:
config.load()["test"]
"""

import warnings
import json
import os

from gourdscan.lib.settings import CHECK_CONF_FILE
from gourdscan.lib.settings import RULES_CONF_FILE
from gourdscan.lib.settings import RULES_PATH


warnings.filterwarnings("ignore")


def load():
    with open(CHECK_CONF_FILE) as con:
        conf = json.load(con)
        return conf


def update(conf):
    with open(CHECK_CONF_FILE, 'w') as con:
        content = json.dumps(conf).replace("{", "{\n").replace("}", "\n}").replace(", ", ",\n").replace("'", '"')
        con.write(content)
        return


def load_rule():
    with open(RULES_CONF_FILE) as con:
        conf = json.load(con)
        return conf


def update_rule(rule):
    with open(RULES_CONF_FILE, 'w') as con:
        content = json.dumps(rule)
        con.write(content)


def rule_read(name, get_file_handle=None):
    if get_file_handle:
        return os.path.join(RULES_PATH, name, '.rule')
    with open(os.path.join(RULES_PATH, name, '.rule')) as con:
        content = con.read()
        return content


def rule_write(name, rule):
    with open(os.path.join(RULES_PATH, name, '.rule'), "w") as con:
        con.write(rule)
