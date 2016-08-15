#coding=utf-8
import urllib2
import urllib
import json
import base64
import random
import re
from hashlib import md5
from binascii import b2a_base64 as base64_encode
from urlparse import urlparse as urlps
from connectredis import workerconf
class isqlmap:

    '''
    Communicate with sqlmapapi, post url, data and headers to sqlmapapi.
    self.sqlmapapi: get sqlmapapi url config from redis.
    func send_sqlmap: send url, data and headers to sqlmapapi url.
    func new_task: get taskid from sqlmapapi.
    func extract_request: get all the data from selfscan.py and start the sqlmap scan, return taskid and sqlmapapi url.
    '''

    def __init__(self):
        self.sqlmap_config={'tech':'BT'}
        self.sqlmapapi=""
        self.header_agent='x'
        
    def send_sqlmap(self,url,data):
        if(str(data))=="GET":
            sqlreq=urllib2.urlopen(url).read()
        else:
            print "[*] send to sqlmap"
            req=urllib2.Request(url, data) 
            req.add_header("Content-Type","application/json")
            sqlreq = urllib2.urlopen(req).read()
        return sqlreq
    def new_task(self):       
        task=self.send_sqlmap(self.sqlmapapi+"/task/new",'GET')
        task_id=json.loads(task)
        task_id=task_id['taskid']    
        return task_id
    def send_inject(self,task_id,send_data):    
        self.send_sqlmap(self.sqlmapapi+"/scan/"+task_id+"/start",send_data)
    def post_sqlmap(self,url,headers,body,raw_request):
        request_user_agent=headers['User-Agent']
        post_data={"url":url,"data":body,'user-agent':request_user_agent}
        if 'Cookie' in headers.keys():
            post_data={"url":url,"cookie":headers['Cookie'],"data":body,'user-agent':request_user_agent}
        post_data.update(self.sqlmap_config)
        post_data=json.dumps(post_data)    
        taskid=self.new_task()       
        self.send_inject(taskid,post_data)
        return taskid
    def get_sqlmap(self,url,headers,raw_request):
        request_user_agent=headers['User-Agent']
        #userhash=headers['userhash']
        post_data={"url":url,'user-agent':request_user_agent}
        if 'Cookie' in headers.keys():
            post_data={"url":url,"cookie":headers['Cookie'],'user-agent':request_user_agent}
        post_data.update(self.sqlmap_config)
        post_data=json.dumps(post_data)    
        taskid=self.new_task()
        self.send_inject(taskid,post_data) 
        return taskid
    def get_sqlmapapi(self):
        sqlmapapis = workerconf["sqlmapapi_cluster"]
        return random.sample(sqlmapapis, 1)[0]
    def extract_request(self,url,method,headers,body):
        self.sqlmapapi = self.get_sqlmapapi()
        requests="%s %s\r\n"%(method,url)   
        for key,value in headers.items():
            requests+="%s: %s\r\n"%(key,value)
        if body:
            requests+="\r\n%s"%body
        if method.upper()=='POST':
            taskid=self.post_sqlmap(url,headers,body,requests)
        if method.upper()=='GET':
            taskid=self.get_sqlmap(url,headers,requests)
        return taskid, self.sqlmapapi
