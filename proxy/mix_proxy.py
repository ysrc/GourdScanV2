#!/usr/bin/env python
#coding: utf-8

import re
import ssl
import socket
import warnings
import requests
import threading

from lib.settings import CONF_PATH
from lib.redisopt import conn, content_deal
from lib import config

warnings.filterwarnings("ignore")

"""
Mix proxy with HTTP and HTTPS.
Use local key file and cert file to get https flow.
If there is a "connect" method first, then https it is.
Else it's a http packet.
Request to remote server with python requests lib.
Put requests into redis server to scan.
Black_domain and black_ext had wroten into this script.
White_domain are loaded from white_domain.conf split by "," in one line!
"""


def https_things(sock):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.load_cert_chain(certfile=CONF_PATH + "key.crt", keyfile=CONF_PATH + "key.pem")
    connstream = context.wrap_socket(sock, server_side=True)
    client_conn(connstream, True)


def get_str(res):
    code = str(res.status_code)
    reason = res.reason
    data = ''
    headers = res.headers
    wrong_head = ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding']
    for i in wrong_head:
        if i in headers.keys():
            del headers[i]
    headers['Content-Length'] = len(res.content)
    data += 'HTTP/1.1 %s %s\r\n' % (code, reason)
    for key in res.headers.keys():
        data += '%s: %s\r\n' % (key, headers[key])
    data += '\r\n' + res.content
    return data


def get_res(data, connstream, https):
    try:
        headers = {}
        post = ''
        if data[0:7] == 'CONNECT':
            connstream.sendall("HTTP/1.1 200 Connection established\r\n\r\n")
            https_things(connstream)
            return
        if not re.search('(GET|POST) (.*) HTTP', data):
            return

        methods = re.findall('(GET|POST) (.*) HTTP', data)[0]
        url = methods[1]
        method = methods[0]

        if method == 'GET':
            head = data.split('\r\n')[1:]
            for h in head:
                if ': ' in h[2:]:
                    headers[h.split(': ')[0]] = h.split(': ')[1]
            host = headers['Host'].replace(' ', '')

            if not https:
                uri = url
            else:
                uri = "https://%s%s" % (host, url)
            print uri
            content_deal(headers, host, method, postdata='', uri=uri, packet=data)

            if 'Host' in headers.keys():
                del headers['Host']

            res = requests.get(uri, headers=headers, verify=False)
            response = get_str(res)
            connstream.sendall(response)
            connstream.close()
            return

        elif method == 'POST':
            body = data.split('\r\n\r\n')[1]
            head = data.split('\r\n\r\n')[0].split('\r\n')[1:]
            for h in head:
                if ': ' in h[2:]:
                    headers[h.split(': ')[0]] = h.split(': ')[1]
            host = headers['Host'].replace(' ', '')

            if not https:
                uri = url
            else:
                uri = "https://%s%s" % (host, url)
            print uri
            content_deal(headers, host, method, postdata=body, uri=uri, packet=data)

            if 'Host' in headers.keys():
                del headers['Host']
                
            res = requests.post(uri, headers=headers, data=body, verify=False)
            response = get_str(res)
            connstream.sendall(response)
            connstream.close()
            return

    except Exception, e:
        if 'url' in dir():
            print url
        print "Http Error: " + str(e)
        try:
            err = "HTTP/1.1 500 Internal Server Error\r\n"
            err += "Content-Length-Type: text/html;\r\n"
            err += "Content-Length: 17\r\n\r\n"
            err += "HTTP Error"
            connstream.sendall()
            connstream.close()
        except Exception as e:
            pass


def client_conn(connstream, https=False):
    try:
        connstream.settimeout(2)
        data = ""
        while True:
            tmp = connstream.recv(10240)
            data += tmp
            if tmp == '':
                break
    except Exception as e:
        pass
    connstream.settimeout(10)
    get_res(data, connstream, https)


def main():
    try:
        addr = config.load()['mix_addr']
        port = int(config.load()['mix_port'])
        bindsocket = socket.socket()
        bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bindsocket.bind((addr, port))
        bindsocket.listen(300)
    except Exception as e:
        conf = config.load()
        conf['mix_stat'] = "false"
        config.update(conf)
        print e
        exit()
    while config.load()['mix_stat'].lower() == "true":
        try:
            connstream, fromaddr = bindsocket.accept()
            t = threading.Thread(target=client_conn, args=(connstream,))
            t.start()
        except Exception as e:
            print e
            if 'connstream' in dir():
                connstream.close()
    bindsocket.close()
