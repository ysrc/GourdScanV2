#/usr/bin/env python 

import platform

'''
print good or error message
'''

def good(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;32m'
        endc = '\033[0m'
        print "[+] " + color + msg + endc
    else:
        print "[+] " + msg

def warning(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;37m'
        endc = '\033[0m'
        print "[*] " + color + msg + endc
    else:
        print "[+] " + msg

def error(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;31m'
        endc = '\033[0m'
        print "[*] " + color + msg + endc
    else:
        print "[+] " + msg

def jump(url):
    return "<script>window.location.href=\"%s\"</script>" % url