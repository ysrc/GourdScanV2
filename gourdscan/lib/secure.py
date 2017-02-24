#!/usr/bin/env python 
# coding: utf-8

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
