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
        except:
            exit('Something going wrong with pip, please run "pip install requests tornado redis scapy" manualy!')