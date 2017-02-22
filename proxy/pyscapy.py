#!/usr/bin/env python
#coding: utf-8
import os
import sys
import time
import json
import base64
import logging
import requests
from hashlib import md5
sys.path.append("..")
from lib.lib_redis import conn, content_deal
from lib import lib_out as out
from lib import lib_config
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

'''
capture: capture packets on the adapter given, and put those into redis.
'''

def extract(data, out):
    try:
        methods = re.findall('(GET|POST) (.*) HTTP',data)[0]
        url = methods[1]
        method = methods[0]
        headers = {}
        if method == 'GET':
            head = data.split('\r\n')[1:]
            for h in head:
                if ': ' in h[2:]:
                    headers[h.split(': ')[0]] = h.split(': ')[1]
            host = headers['Host'].replace(' ', '')
            uri = "http://%s%s" % (host, url)
            if out:
                print "%s   %s" % (method, uri)
            content_deal(headers, host, method, postdata = '', uri = uri, packet = data)
            return

        elif method == 'POST':
            body = data.split('\r\n\r\n')[1]
            head = data.split('\r\n\r\n')[0].split('\r\n')[1:]
            for h in head:
                if ': ' in h[2:]:
                    headers[h.split(': ')[0]] = h.split(': ')[1]
            host = headers['Host'].replace(' ', '')
            uri = "http://%s%s" % (host, url)
            if out:
                print "%s   %s" % (method, uri)
            content_deal(headers, host, method, postdata = body, uri = uri, packet = data)

            return

    except Exception, e:
        if 'url' in dir() and "method" in dir():
            print "%s   %s" % (method, uri)
        print "Http Error: " + str(e)
        return

def print_request(http):
    print "%s   %s%s    %s" % (http.method, http.host, http.url, http.hash)

def capture(x):
    out = lib_config.load()['scapy_out']
    if lib_config.load()['scapy_stat'].lower() == 'false':
        raise Exception('scapy', 'out')
    if 'HTTP/' in x.lastlayer().original and x.lastlayer().original[0:4] != 'HTTP':
        body = x.lastlayer().original
        http = extract(body, out)
            
def main():
    NIC = lib_config.load()["scapy_network_card"]#network adapter name
    try:
        if NIC == 'all':
            sniff(filter="tcp",prn=lambda x:capture(x))
        else:
            sniff(iface=NIC,filter="tcp",prn=lambda x:capture(x))
    except Exception,e:
        out.error("scapy out!")
        conf = lib_config.load()
        conf['scapy_stat'].lower = "false"
        lib_config.update(conf)
    finally:
        return