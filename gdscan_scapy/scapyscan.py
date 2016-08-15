#!/usr/bin/env python
#coding: utf-8
import os
import sys
import time
import json
import base64
import requests
from scapy.all import *
from hashlib import md5
from lib.connectredis import r
from lib.raw2http import Http_body as Http

'''
capture: capture packets on the adapter given, and put those into redis.
'''

def print_help():
    print 'Usage:'
    print '    python %s eth0(network adapter name or \'all\') out/none(output scapy detail)' % sys.argv[0]
    print 'Example:'
    print '    python %s eth0 out' % sys.argv[0]
    print '    python %s * out' % sys.argv[0]
    exit()

def print_request(http):
    print "%s   %s%s    %s" % (http.method, http.host, http.url, http.hash)

def capture(x):
    global out
    if 'HTTP/' in x.lastlayer().original and x.lastlayer().original[0:4] != 'HTTP':
        body = x.lastlayer().original
        http = Http(body)
        if http.extract() and 'Gdscan' not in http.headers.keys():
            if out:
                print_request(http)
            request={'headers':http.headers,'host':http.host,'url':http.url,'method':http.method,'postdata':http.headers['postdata'],'hash':http.hash}
            reqhash = request['hash']
            b64req = base64.encodestring(json.dumps(request))
            if r.hsetnx("request", reqhash, b64req):
                r.lpush("waiting", reqhash)
            
if __name__ == "__main__":
    NIC = ''#network adapter name
    global out
    if len(sys.argv) < 2:
        print_help()
    elif len(sys.argv) == 2:
        out = True
    else:
        if sys.argv[2].lower() == 'none':
            out = False
        else:
            out = True
    NIC = sys.argv[1]
    try:
        if NIC == 'all':
            sniff(filter="tcp",prn=lambda x:capture(x))
        else:
            sniff(iface=NIC,filter="tcp",prn=lambda x:capture(x))
    except Exception,e:
        print e
