#!/usr/bin/env python 
# coding: utf-8

import os
import time

import md5

from lib import config
from lib.settings import SESSION_CONF_FILE

'''
Create session string or update a session into session file.
Control the length of session file to make sure it will not be too big.
Destroy a session string to make it logout.
'''


def new(ip):
    return md5.new(config.load()["cookie_secret"] + str(time.time()) + ip).hexdigest()


def check(session):
    with open(SESSION_CONF_FILE, 'r+') as f:
        lines = f.readlines()
        f.close()
        for line in lines:
            if session == line.strip():
                return True
        return False


def update(session):
    size_control()
    with open(SESSION_CONF_FILE, 'a') as f:
        f.write(session + '\n')
        f.close()
        return True


def destroy(session):
    with open(SESSION_CONF_FILE, 'r') as f:
        lines = f.readlines()
        f.close()
        ff = open(SESSION_CONF_FILE, 'w')
        for line in lines:
            if session != line.strip():
                ff.write(line)
        ff.close()
        return True


def size_control():
    if os.path.getsize(SESSION_CONF_FILE) > config.load()["session_size"]:
        with open(SESSION_CONF_FILE, 'r') as f:
            lines = f.readlines()
            f.close()
            ff = open(SESSION_CONF_FILE, 'w')
            size = 0
            for line in lines:
                size += len(line)
                if size < config.load()["session_size"]:
                    ff.write(line)
                else:
                    ff.close()
                    return
            print size
            ff.close()
