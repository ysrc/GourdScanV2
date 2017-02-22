#!/usr/bin/env python 
#coding: utf-8

import requests
import lib_config
import lib_out

'''
Checking update when it start
'''

def check_update():
    lib_out.good("Checking update...")
    try:
        res = requests.get(lib_config.load()['check_url'], timeout=10)
        version = res.content
        if version != lib_config.load()['version']:
            update()
            return True
        else:
            return False
    except:
        lib_out.error("Can not connect to update server!")
        return False
        
def update():
    lib_out.warning("New version is ok!")
    lib_out.warning("Please update Gourdscan with git(git pull https://github.com/ysrc/GourdScanV2.git)")
    
