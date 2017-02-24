#!/usr/bin/env python 
# coding: utf-8

from gourdscan import VERSION
from gourdscan.web.app import main
from gourdscan.lib.update import check_update


# check update
check_update()

logo = """
   _____                              _
  / ____|                            | |
 | |  __    ___    _   _   _ __    __| |
 | | |_ |  / _ \  | | | | | '__|  / _` |
 | |__| | | (_) | | |_| | | |    | (_| |
  \_____|  \___/   \__,_| |_|     \__,_|  Ver %s

    Cond0r@Codescan      range@Codescan
""" % VERSION
print logo


if __name__ == '__main__':
    main()
