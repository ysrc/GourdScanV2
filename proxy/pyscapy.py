#!/usr/bin/env python
# coding: utf-8

"""
capture: capture packets on the adapter given, and put those into redis.
"""

import re
import logging

from scapy.all import *

from lib.redisopt import conn, content_deal
from lib.out import error
from lib import config


logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


def extract(data, out):
    try:
        methods = re.findall('(GET|POST) (.*) HTTP', data)[0]
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
            if out == 'true':
                print_request(method, host, url)
            content_deal(headers, host, method, postdata='', uri=uri, packet=data)

        elif method == 'POST':
            body = data.split('\r\n\r\n')[1]
            head = data.split('\r\n\r\n')[0].split('\r\n')[1:]
            for h in head:
                if ': ' in h[2:]:
                    headers[h.split(': ')[0]] = h.split(': ')[1]
            host = headers['Host'].replace(' ', '')
            uri = "http://%s%s" % (host, url)
            if out == 'true':
                print_request(method, host, url)
            content_deal(headers, host, method, postdata=body, uri=uri, packet=data)

    except Exception, e:
        if 'url' in dir() and "method" in dir():
            print "%s   %s" % (method, uri)
        print "Http Error: " + str(e)


def print_request(method, host, url):
    print "%s   %s%s" % (method, host, url)


def capture(x):
    out = config.load()['scapy_out'].lower()
    if config.load()['scapy_stat'].lower() == 'false':
        raise Exception('scapy', 'out')
    if 'HTTP/' in x.lastlayer().original and x.lastlayer().original[0:4] != 'HTTP':
        body = x.lastlayer().original
        http = extract(body, out)


def main():
    NIC = config.load()["scapy_network_card"]  # network adapter name
    try:
        if NIC == 'all':
            sniff(filter="tcp", prn=lambda x: capture(x))
        else:
            sniff(iface=NIC, filter="tcp", prn=lambda x: capture(x))
    except Exception as e:
        error("scapy out!")
        conf = config.load()
        conf['scapy_stat'] = "false"
        config.update(conf)
