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
import socket

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.httpclient
import tornado.httputil

from urlparse import urlparse

from lib import config
from lib.redisopt import conn, content_deal


logger = logging.getLogger('tornado_proxy')
__all__ = ['ProxyHandler', 'run_proxy']


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

    def deal(method):
        def wrapper(self, *args, **kwargs):
            if config.load()['tornado_stat'].lower() == "false":
                return
            return method(self, *args, **kwargs)
        return wrapper

    def compute_etag(self):
        return None  # disable tornado Etag

    def extract_request(self, url, headers, method, body):
        requests = "%s %s\r\n" % (method, url)
        for key, value in headers.items():
            requests += "%s: %s\r\n" % (key, value)
        requests += "\r\n%s" % body
        return requests
    
    @deal
    @tornado.web.asynchronous
    def get(self):
        try:
            logger.debug('Handle %s request to %s', self.request.method,
                         self.request.uri)

            def handle_response(response):
                if (response.error and not
                        isinstance(response.error, tornado.httpclient.HTTPError)):
                    self.set_status(500)
                    self.write('Internal server error:\n' + str(response.error))
                else:
                    self.set_status(response.code, response.reason)
                    self._headers = tornado.httputil.HTTPHeaders()  # clear tornado default header

                    for header, v in response.headers.get_all():
                        if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                            self.add_header(header, v)  # some header appear multiple times, eg 'Set-Cookie'

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
                uri = self.request.uri
                headers = dict(self.request.headers)
                data = self.extract_request(uri, headers, self.request.method, body)
                host = urlparse(uri).netloc
                content_deal(headers, host, self.request.method, postdata=body, uri=uri, packet=data)

            except tornado.httpclient.HTTPError as e:
                if hasattr(e, 'response') and e.response:
                    handle_response(e.response)
                else:
                    self.set_status(500)
                    self.write('Internal server error:\n' + str(e))
                    self.finish()
        except:
            return

    @deal
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


def run_proxy(port, address):
    """
    Run proxy on the specified port. If start_ioloop is True (default),
    the tornado IOLoop will be started immediately.
    """
    app = tornado.web.Application([
        (r'.*', ProxyHandler),
    ])
    app.listen(port=port, address=address)


def main():
    port = int(config.load()['tornado_port'])
    address = config.load()['tornado_address']
    print ("Starting HTTP proxy on port %d" % port)
    run_proxy(port, address)
