#!/usr/bin/env python

import sys
import ctypes
import platform

'''
print good or error message
'''

def windows_out(color, msg):
    STD_OUTPUT_HANDLE = -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, color)
    print msg
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, 0x0c|0x0a|0x09)

def good(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;32m'
        endc = '\033[0m'
        print "[+] " + color + msg + endc
    else:
        windows_out(0x0a, "[+] %s" % msg)


def warning(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;37m'
        endc = '\033[0m'
        print "[*] " + color + msg + endc
    else:
        windows_out(0x06, "[*] %s" % msg)

def error(msg):
    if "Windows" not in platform.platform():
        color = '\033[01;31m'
        endc = '\033[0m'
        print "[*] " + color + msg + endc
    else:
        windows_out(0x0c, "[+] %s" % msg)

def jump(url):
    return "<script>window.location.href=\"%s\"</script>" % url

def alert(content, url):
    return "<script>alert(\"%s\");window.location.href=\"%s\"</script>" % (content, url)
