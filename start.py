#!/usr/bin/env python 
#coding: utf-8

from views import views
from lib import lib_update

#check update
lib_update.check_update()

logo='''
   _____                              _
  / ____|                            | |
 | |  __    ___    _   _   _ __    __| |
 | | |_ |  / _ \  | | | | | '__|  / _` |
 | |__| | | (_) | | |_| | | |    | (_| |
  \_____|  \___/   \__,_| |_|     \__,_|  Ver 2.1

    Cond0r@Codescan      range@Codescan  
 '''
print logo

#start web app
views.main()
