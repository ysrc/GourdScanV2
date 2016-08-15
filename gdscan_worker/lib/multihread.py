#coding=utf-8
import threading
class multi(threading.Thread):
    def __init__(self,function,args):
        threading.Thread.__init__(self)
        self.function=function
        self.args=args
    def run(self):
        self.function(self.args)

def multi_thread(function,args,num):
    for i in xrange(num):
        multi(function,args).start()
