#coding=utf-8
from raw2http import Http_body as Http
from Queue import Queue
from time import sleep
import subprocess
import os
savepath = "/home/raw/"
class tcpflow:

    '''
    Capture packets with tcpflow and change it into headers, body, method, etc.
    '''

    def __init__(self):
        self.Request_Queue=Queue()
        self.Old_Queue=Queue()
        #self.path=os.path.join(os.path.dirname(__file__), '../raw/')
        self.path=savepath
        self.cmd='tcpflow -i eth0  tcp[20:2]=0x4745 or tcp[20:2]=0x4854 or tcp[20:2]=0x504f -o '+self.path
        self.http=Http('')
    def run_tcpflow(self):
        self.sub=subprocess.Popen(self.cmd,shell=True)
        return True
    def close_tcpflow(self):
        self.close()
    def listdir(self):
        file_list=[]
        files=os.listdir(self.path)
        for file in files:
            if file[0]!='.':
                file_list.append(file)
        return file_list
    def addQueue(self,file_list):
        for _file in file_list:
            _file=savepath+_file
            if 'xml' in _file or '.txt' in _file:
                continue#return False
            with open(_file) as io:
                data=io.read()
            #os.remove(_file)
            os.system("rm -f %s"%_file)
            http=self.http
            http.setbody(data)
            if 'Gdscan' not in http.headers.keys() and http.extract():
                request={'headers':http.headers,'host':http.host,'url':http.url,'method':http.method,'postdata':http.headers['postdata'],'hash':http.hash}
                self.Request_Queue.put(request)
            else:
                request={}