#!/usr/bin/env python 
# coding: utf-8

import os
import cgi
import socket

'''
Some func to make the system stable
'''


def clear(s):
    return cgi.escape(s).replace("'", "&quot;").replace('"', "\&quot;")


def kill(addr, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    sock.send(data)
    sock.recv(102400)

def check_requirements():
    try:
        import requests
        import tornado
        import redis
        import scapy
    except:
        yes = raw_input('Do you want to install those module with the command "pip install"? (Y/n)')
        if yes == '' or yes.lower() == 'y' or yes.lower() == 'yes':
            os.system("pip install requests tornado redis scapy")
        try:
            import requests
            import tornado
            import redis
            import scapy
            print "Requirements is OK!"
            return
        except Exception, e:
            exit('Something going wrong with pip: %s, please run "pip install requests tornado redis scapy" manualy!' % e)

def check_redis():
    try:
        from lib.redisopt import conn
    except:
        yes = raw_input('Something wrong with the redis, Do you want to run the command "redis-server ./conf/redis.conf"? (Y/n)')
        if yes == '' or yes.lower() == 'y' or yes.lower() == 'yes':
            os.system("redis-server ./conf/redis.conf")
        try:
            from lib.redisopt import conn
        except Exception, e:
            exit("Something wrong with the redis: %s, please check it manualy!" % e)