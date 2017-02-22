#coding: utf-8

import warnings
import json
import os

warnings.filterwarnings("ignore")
'''
Config and update/reload file
get test param:
lib_config.load()["test"]
'''
ROOT = os.path.dirname(os.path.abspath(__file__))

def load():
    with open(ROOT+os.path.sep+".."+os.path.sep+"conf.json") as con:
        conf = json.load(con)
        con.close()
        return conf

def update(conf):
    with open(ROOT+os.path.sep+".."+os.path.sep+"conf.json", 'w') as con:
        content = json.dumps(conf).replace("{", "{\n").replace("}", "\n}").replace(", ", ",\n").replace("'", '"')
        con.write(content)
        con.close()
        return

def load_rule():
    with open(ROOT+os.path.sep+".."+os.path.sep+"rules"+os.path.sep+"rule.conf") as con:
        conf = json.load(con)
        con.close()
        return conf

def update_rule(rule):
    with open(ROOT+os.path.sep+".."+os.path.sep+"rules"+os.path.sep+"rule.conf", 'w') as con:
        content = json.dumps(rule)
        con.write(content)
        con.close()
        return

def rule_read(name, get_file_handle=None):
    if get_file_handle != None:
        return ROOT+os.path.sep+".."+os.path.sep+"rules"+os.path.sep+name+".rule"
    with open(ROOT+os.path.sep+".."+os.path.sep+"rules"+os.path.sep+name+".rule") as con:
        content = con.read()
        con.close()
        return content

def rule_write(name, rule):
    with open(ROOT+os.path.sep+".."+os.path.sep+"rules"+os.path.sep+name+".rule", "w") as con:
        con.write(rule)
        con.close()
        return