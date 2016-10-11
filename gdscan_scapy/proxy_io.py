#!/usr/bin/env python
#
# Simple asynchronous HTTP proxy with tunnelling (CONNECT).
#
# GET/POST proxying based on
# http://groups.google.com/group/python-tornado/msg/7bea08e7a049cf26
#
# Copyright (C) 2012 Senko Rasic <senko.rasic@dobarkod.hr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import os
import sys
import socket
from urlparse import urlparse
import threading
import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient
import tornado.httputil
from hashlib import md5
from lib.connectredis import r
from base64 import encodestring as es
import json
logger = logging.getLogger('tornado_proxy')

__all__ = ['ProxyHandler', 'run_proxy']
logo='''
   _____                              _
  / ____|                            | |
 | |  __    ___    _   _   _ __    __| |
 | | |_ |  / _ \  | | | | | '__|  / _` |
 | |__| | | (_) | | |_| | | |    | (_| |
  \_____|  \___/   \__,_| |_|     \__,_|

    Cond0r@Codescan      Ver 2.0

 '''

print logo
def get_proxy(url):
    url_parsed = urlparse(url, scheme='http')
    proxy_key = '%s_proxy' % url_parsed.scheme
    return os.environ.get(proxy_key)


def parse_proxy(proxy):
    proxy_parsed = urlparse(proxy, scheme='http')
    return proxy_parsed.hostname, proxy_parsed.port


def fetch_request(url, callback, **kwargs):
    proxy = get_proxy(url)
    if proxy:
        logger.debug('Forward request via upstream proxy %s', proxy)
        tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')
        host, port = parse_proxy(proxy)
        kwargs['proxy_host'] = host
        kwargs['proxy_port'] = port

    req = tornado.httpclient.HTTPRequest(url, **kwargs)
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch(req, callback, raise_error=False)

class ProxyHandler(tornado.web.RequestHandler):
    def compute_etag(self):
        return None # disable tornado Etag
    def extract_request(self,url,method,headers,body):
        requests="%s %s\r\n"%(method,url)
        for key,value in headers.items():
            requests+="%s: %s\r\n"%(key,value)
        if body:
            requests+="\r\n%s"%body
        #print requests
    def get_hash(self, host, postdata):
        request = 'http://' + host + urlparse(self.request.uri).path + "?"
        dic = urlparse(self.request.uri).query.split('&')
        for d in dic:
            request += d.split('=')[0]+'=&'
        request += "|"
        for d in postdata.split('&'):
            request += d.split('=')[0]+'=&'
        url_hash = md5(request).hexdigest()
        return url_hash
    def insert_redis(self, b64req, hash, host):
        path = self.request.uri.split('?')[0]
        black_ext='css,flv,mp4,mp4,swf,js,jpg,jpeg,png,css,mp4,gif,txt,ico,pdf,css3,txt,rar,zip,avi,mp4,swf,wmi,exe,mpeg,ppt,pptx,doc,docx,xls,xlsx'
        black_domain='ditu.google.cn,doubleclick,cnzz.com,baidu.com,40017.cn,google-analytics.com,googlesyndication,gstatic.com,bing.com,google.com,digicert.com'
        with open('white_domain.conf') as white:
            white_domain = white.readline().strip('\n').strip('\r')
            if white_domain != "":
                for domain in white_domain.split(','):
                    if not re.search(white_domain,host.lower()):
                        return
            else:
                pass

        for ext in black_ext.split(','):
            if path.lower().endswith(ext):
                return
        for domain in black_domain.split(','):
            if host.lower().split(':')[0].endswith(domain):
                return
        if r.hsetnx("request", hash, b64req):
            r.lpush("waiting", hash)

    @tornado.web.asynchronous
    def get(self):
        logger.debug('Handle %s request to %s', self.request.method,
                     self.request.uri)

        def handle_response(response):
            if (response.error and not
                    isinstance(response.error, tornado.httpclient.HTTPError)):
                self.set_status(500)
                self.write('Internal server error:\n' + str(response.error))
            else:
                self.set_status(response.code, response.reason)
                self._headers = tornado.httputil.HTTPHeaders() # clear tornado default header

                for header, v in response.headers.get_all():
                    if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                        self.add_header(header, v) # some header appear multiple times, eg 'Set-Cookie'

                if response.body:
                    self.set_header('Content-Length', len(response.body))
                    self.write(response.body)
                    #print 11
            self.finish()

        body = self.request.body

        if not body:
            body = ""
        try:
            if 'Proxy-Connection' in self.request.headers:
                del self.request.headers['Proxy-Connection']


            fetch_request(
                self.request.uri, handle_response,
                method=self.request.method, body=body,
                headers=self.request.headers, follow_redirects=False,
                allow_nonstandard_methods=True)
            request_dict={}
            request_dict['uri']=self.request.uri
            request_dict['method']=self.request.method
            request_dict['headers']=dict(self.request.headers)
            request_dict['body']=body
            request_dict['postdata'] = request_dict['body']
            url=urlparse(request_dict['uri'])
            request_dict['host']= url.netloc
            request_dict['url']= request_dict['uri'].split(url.netloc)[-1]
            request_dict['hash']= self.get_hash(request_dict['host'], request_dict['postdata'])
            #print "="*10, "Got one:", request_dict
            b64req =  es(json.dumps(request_dict))
            self.insert_redis(b64req, request_dict['host'], request_dict['host'])

        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write('Internal server error:\n' + str(e))
                self.finish()

    @tornado.web.asynchronous
    def post(self):
        return self.get()

    @tornado.web.asynchronous
    def connect(self):
        logger.debug('Start CONNECT to %s', self.request.uri)
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        def read_from_client(data):
            upstream.write(data)

        def read_from_upstream(data):
            client.write(data)

        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()

        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()

        def start_tunnel():
            logger.debug('CONNECT tunnel established to %s', self.request.uri)
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')

        def on_proxy_response(data=None):
            if data:
                first_line = data.splitlines()[0]
                http_v, status, text = first_line.split(None, 2)
                if int(status) == 200:
                    logger.debug('Connected to upstream proxy %s', proxy)
                    start_tunnel()
                    return

            self.set_status(500)
            self.finish()

        def start_proxy_tunnel():
            upstream.write('CONNECT %s HTTP/1.1\r\n' % self.request.uri)
            upstream.write('Host: %s\r\n' % self.request.uri)
            upstream.write('Proxy-Connection: Keep-Alive\r\n\r\n')
            upstream.read_until('\r\n\r\n', on_proxy_response)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)

        proxy = get_proxy(self.request.uri)
        if proxy:
            proxy_host, proxy_port = parse_proxy(proxy)
            upstream.connect((proxy_host, proxy_port), start_proxy_tunnel)
        else:
            upstream.connect((host, int(port)), start_tunnel)


def run_proxy(port, start_ioloop=True):
    """
    Run proxy on the specified port. If start_ioloop is True (default),
    the tornado IOLoop will be started immediately.
    """
    app = tornado.web.Application([
        (r'.*', ProxyHandler),
    ])
    app.listen(port)
    ioloop = tornado.ioloop.IOLoop.instance()
    if start_ioloop:
        ioloop.start()

if __name__ == '__main__':
    port = 10806
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    print ("Starting HTTP proxy on port %d" % port)
    run_proxy(port)
