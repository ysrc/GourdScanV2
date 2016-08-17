import re
from hashlib import md5
from urlparse import parse_qs as parse_url
from urlparse import urlparse
class Http_body:

    '''
    Translate http socket packets into headers and body, method, etc.
    '''

    def __init__(self,body):
        #threading.Thread.__init__(self)
        self.body=body
        self.headers={}
        self.method=''
        self.host=''
        self.url=''
    def setbody(self,body):
        self.body=body
    def sethash(self):
        request = 'http://' + self.host + self.url.split('?')[0]
        dic = urlparse.urlparse('http://'+self.host+self.url).query.split('&')
        for d in dic:
            request += d.split('=')[0]+'=&'
        request += "|"
        for d in self.headers['postdata'].split('&'):
            request += d.split('=')[0]+'=&'
        self.hash=md5(request).hexdigest()

    def is_ok(self,url):
        request=urlparse(url)
        path=request.path
        path=path.split(".")[-1].lower().replace(' ','')
        #print path,url
        black_ext='css,flv,mp4,mp4,swf,js,jpg,jpeg,png,css,mp4,gif,txt,ico,flv,js,css,jpg,png,jpeg,gif,pdf,css3,txt,rar,zip,avi,mp4,swf,wmi,exe,mpeg,ppt,pptx,doc,docx,xls,xlsx'
        black_domain='ditu.google.cn,doubleclick,cnzz.com,baidu.com,40017.cn,google-analytics.com,googlesyndication,gstatic.com,bing.com,google.com,digicert.com'
        with open('../white_domain.conf') as white:
            white_domain = white.readline().strip('\n').strip('\r')
            if white_domain != "":
                for domain in white_domain.split(','):
                    if not re.search(white_domain,request.netloc.lower()):
                        return
            else:
                pass
        if path.lower() in black_ext.split(','):
            return False

        host=request.hostname.lower()
        for h in black_domain.split(','):
            if h in host:
                return False
        return True
    def extract(self):

        request=self.body
        try:
            method=re.findall('(GET|POST) (.*) HTTP',request)[0]
            url=method[1]
        except:
            #print "[*]Not Http Request!"
            return False

        method=method[0]
        headers={}
        body=''
        if method=='GET':
            head=request.split("\r\n")[1:]
            headers.update({'postdata':''})
            for h in head:
                if ': ' in h:
                    h=h.split(": ")
                    headers.update({h[0]:h[1]})
        if method=='POST':
            try:
                body=request.split("\r\n\r\n")[1]
                headers.update({'postdata':body})
                request=request.split("\r\n\r\n")[0]
                head=request.split("\r\n")[1:]
                for h in head:
                    if ': ' in h:
                        h=h.split(": ")
                        headers.update({h[0]:h[1]})
            except:
                pass

        self.headers=headers
        self.host=headers['Host'].replace(' ','')
        self.method=method
        self.url=url
        self.sethash()
        request='http://'+self.host+url
        #print request
        if self.is_ok(request):
            return True
        return False
