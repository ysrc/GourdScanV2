#!/usr/bin/env python 
# coding: utf-8

import requests

from lib import config
from lib import out

'''
Checking update when it start
'''


def check_update():
    out.good("Checking update...")
    try:
        res = requests.get(config.load()['check_url'], timeout=10)
        version = res.content
        if version != config.load()['version']:
            update()
            return True
        else:
            return False
    except:
        out.error("Can not connect to update server!")
        return False


def update():
    out.warning("New version is ok!")
    out.warning("Please update Gourdscan with git(git pull https://github.com/ysrc/GourdScanV2.git)")
