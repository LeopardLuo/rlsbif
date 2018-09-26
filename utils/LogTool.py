#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import logging.config
import os, ctypes
from ctypes import *

FOREGOUNG_WHITE = 0X0007
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_DARKPINK = 0x05 # dark pink.
FOREGROUND_DARKRED = 0x04 # dark red.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

STD_OUTPUT_HANDLE = -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  
def set_color(color=FOREGOUNG_WHITE, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

class Logger(object):
    
    def __init__(self, clevel = logging.DEBUG, flevel = logging.DEBUG):        
        if 'testcases' in os.getcwd() or 'utils' in os.getcwd():
            path1 = os.path.join(os.path.dirname(os.getcwd()), 'report')
        else:
            path1 = os.path.join(os.getcwd(), 'report')
        if not os.path.exists(path1):
            os.makedirs(path1)
        logfile = os.path.join(path1, 'test.log')
        if not os.path.exists(logfile):
            fh = open(logfile, 'w')
            fh.close()
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        # config console log handler
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        # config file log handler
        fh = logging.handlers.RotatingFileHandler(logfile,'a',20000000,3,)
        fh.setFormatter(fmt)
        fh.setLevel(flevel)

        if not self.logger.handlers:
            self.logger.addHandler(sh)
            self.logger.addHandler(fh)
    
    def debug(self, msg):
        self.logger.debug(msg)
        
    def info(self, msg):
        self.logger.info(msg)    
    
    def warn(self, msg, color=FOREGROUND_YELLOW):
        set_color(color)
        self.logger.warn(msg)
        set_color()
        
    def error(self, msg, color=FOREGROUND_RED):
        set_color(color)
        self.logger.error(msg)
        set_color()
    
    def critical(self, msg, color=FOREGROUND_DARKRED):
        set_color(color)
        self.logger.critical(msg)
        set_color()
    

def getLogger(name):
    if 'testcases' in os.getcwd() or 'utils' in os.getcwd():
        path1 = os.path.join(os.path.dirname(os.getcwd()), 'config')
        logfile = os.path.join(path1, 'logging.conf')
    else:
        path1 = os.path.join(os.getcwd(), 'config')
        logfile = os.path.join(path1, 'logging_root.conf')
    logging.config.fileConfig(logfile)
    return logging.getLogger(name) 

# if __name__ =='__main__':
#     logyyx = Logger()
#     logyyx.debug('一个debug信息')
#     logyyx.info('一个info信息')
#     logyyx.warn('一个warning信息')
#     logyyx.error('一个error信息')
#     logyyx.critical('一个致命critical信息')
#     logyyx.debug('又一个debug信息')