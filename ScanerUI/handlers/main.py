#!/usr/bin/env python
# -*- coding: utf-8 -*-
from handlers.base import BaseHandler

import logging
logger = logging.getLogger('tc.' + __name__)
import sys
import json, os
from base64 import decodestring as ds
import redis, threading
from settings import ROOT
with open(ROOT+os.path.sep+"conf.json") as conf:
    redisconf = json.load(conf)["redis"]
r = redis.StrictRedis(**redisconf)

class ShowUrlsHandler(BaseHandler):
    def get_recent10reqs(self):
        req10keys = r.lrange("waiting", -5, -1)
        req10keys += r.lrange("running", -5, -1)
        recent10reqs = []
        for reqkey in req10keys:
            reqbs64 = r.hget("request", reqkey)
            reqde64 = json.loads(ds(reqbs64))
            recent10reqs.append(reqde64)
        return recent10reqs
    def get_recent10running(self):
        run10keys = r.lrange("running", -10, -1)
        recent10running = []
        for runkey in run10keys:
            reqbs64 = r.hget("request", runkey)
            reqde64 = json.loads(ds(reqbs64))
            recent10running.append(reqde64)
        return recent10running
    def del_running_in_finish(self):
        for reqhash in r.lrange("finish", 0, -1):
            r.lrem("running", 0, reqhash)
    def get(self):
        threading.Thread(target=self.del_running_in_finish, args=()).start() # refresh running
        recent10reqs = self.get_recent10reqs()
        recent10running = self.get_recent10running()
        vul_num = r.llen("xss")+r.llen("sqli")+r.llen("xpath")+r.llen("ldap")+r.llen("lfi")+r.llen("sqli_time")
        vul = {}
        vul['xss'] = r.llen("xss")
        vul['sqli'] = r.llen("sqli")
        vul['xpath'] = r.llen("xpath")
        vul['ldap'] = r.llen("ldap")
        vul['lfi'] = r.llen("lfi")
        vul['sqli_time'] = r.llen("sqli_time")
        if r.llen("xss") != 0 or r.llen("sqli") != 0 or r.llen("xpath") != 0 or r.llen("ldap") != 0 or r.llen("lfi") != 0 or r.llen("sqli_time") !=0:
            vul['Novul'] = 0
        else:
            vul['Novul'] = 100
        safe_num = r.hlen("request") - vul_num
        self.render("table-urls.html", activenum=1, recent10running=recent10running, recent10reqs=recent10reqs, reqnum=r.hlen("request"), finnum=r.llen("finish"), runnum=r.llen("running"), waitnum=r.llen("waiting"), xssnum=r.llen("xss"), sqlinum=r.llen("sqli"), xpathnum=r.llen("xpath"), ldapnum=r.llen("ldap"), lfinum=r.llen("lfi"), sqli_timenum=r.llen("sqli_time"), vul_num=vul_num, safe_num=safe_num, vulnerability=vul)

class ShowRawHttpHandler(BaseHandler):
    def get(self, hash):
        reqbs64 = r.hget("request", hash)
        '''
        self.set_header("Content-Type", 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename={filename}.txt'.format(filename=hash))'''

        if not reqbs64:
            return self.write("invalid hash, u bad hacker")
        request = json.loads(ds(reqbs64))
        requeststring = "{method} {url}  HTTP/1.1\r\nHost: {host}\r\n".format(method=request["method"], url=request["url"], host=request["host"])
        for key in  request["headers"].keys():
            if key == "Host":
                continue
            requeststring += "{key}: {value}\r\n".format(key=key, value=request["headers"][key])
        if request["method"] == "GET":
            requeststring = requeststring.rstrip("\n").rstrip("\r")
        else:
            requeststring += "\r\n{body}".format(body=request["postdata"])

        url = "http://" + request['host'] + request['url']
        if request['postdata'] == '':
            data = 'NULL'
        else:
            data = request['postdata']

        return self.render("table-hash.html", rstring = requeststring, url = url, data = data, activenum=1)

class ConfHandler(BaseHandler):
    def get(self):
        with open(sys.path[0]+'/../../gdscan_worker/conf.json') as f:
            data = f.read()
        return self.render("conf.html", file=data, activenum=8)


from collections import Counter
class ShowSqliHandler(BaseHandler):
    def filtersite(self, sqlireqs, site):
        newsqlireqs = []
        for itemdict in sqlireqs:
            #print "item",itemdict["host"], "site",site
            if itemdict["host"] == site:
                newsqlireqs.append(itemdict)
        return newsqlireqs
    def get_sqlis(self):
        sqlireqs = []
        reqkeys = r.lrange("sqli", 0, -1)
        for reqkey in reqkeys:
            reqbs64 = r.hget("request", reqkey)
            reqde64 = json.loads(ds(reqbs64))
            sqlireqs.append(reqde64)
        return sqlireqs
    def get(self):
        sqlireqs = self.get_sqlis()
        flag = False
        site = self.get_argument('d', '')
        #print type(site)
        if site:
            flag = True
            sqlireqs = self.filtersite(sqlireqs, site)
        else:
            hosts = []
            for item in sqlireqs:
                hosts.append(item["host"])
            count_hosts = Counter(hosts)
            sqlireqs = count_hosts
        #print "looklook", sqlireqs
        self.render("table-sqli.html", activenum=3, sqlireqs=sqlireqs, detail=flag)

def return_reqs_with_payload(vulntype):
    reqs = []
    reqkeys = r.lrange(vulntype, 0, -1)
    for reqkey in reqkeys:
        reqbs64 = r.hget("request", reqkey)
        reqde64 = json.loads(ds(reqbs64))
        reqde64["payload"] = r.hget("bingo_payload", reqkey)
        reqs.append(reqde64)
    return reqs

class ShowXssHandler(BaseHandler):
    def get(self):
        return self.render("table-xss.html", activenum=2, detailreq=return_reqs_with_payload("xss"))

class ShowXpathHandler(BaseHandler):
    def get(self):
        return self.render("table-xpath.html", activenum=4, detailreq=return_reqs_with_payload("xpath"))

class ShowSqliTimeHandler(BaseHandler):
    def get(self):
        return self.render("table-sqli_time.html", activenum=7, detailreq=return_reqs_with_payload("sqli_time"))

class ShowLdapHandler(BaseHandler):
    def get(self):
        return self.render("table-ldap.html", activenum=5, detailreq=return_reqs_with_payload("ldap"))

class ShowLfiHandler(BaseHandler):
    def get(self):
        return self.render("table-lfi.html", activenum=6, detailreq=return_reqs_with_payload("lfi"))