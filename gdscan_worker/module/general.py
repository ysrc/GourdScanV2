#coding=utf-8
import os
import sys
import json
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from exploit import exploit
class general(exploit):
    def exploit(self):
        if self.method=='GET':
            for u in self.get_payloads:
                for p in self.local_files:
                    us=u.replace('{payload}',p)
                    print us+'||'
                    try:
                        time1=time.time()
                        respone=self.request(us).text
                        time2=time.time()
                        self.time=time2-time1
                        if self.timecheck:
                            if self.time_check():
                                self.payloads=us
                                return True
                    except Exception,ex:
                        print "[!] %s Module With GET Error "%self.name,ex
                        return False
                    if self.check(respone):
                        #print us,self.name
                        self.bingo_payload=us
                        self.bingo_respone=respone
                        return True
        if self.method=='POST':
            for pp in self.post_payload:
                for p in self.local_files:
                    us=pp.replace('{payload}',p)
                    #print us
                    try:
                        time1=time.time()
                        a=self.request(self.url,us)
                        time2=time.time()
                        self.time=time2-time1
                        if self.timecheck:
                            if self.time_check():
                                self.payloads=us
                                return True
                    except Exception,ex:
                        print "[!] %s Module With POST Error "%self.name,ex
                        return False
                    respone=a.text
                    if self.check(respone):
                        self.bingo_payload=us
                        self.bingo_respone=respone
                        #print us,self.name
                        return True
        return False
    def callbak(self):
        print 'call'
