#!/usr/bin/python
# -*-coding:utf-8-*-

import sys
import os
import pytest


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
pPath = os.path.dirname(curPath)
ppPath = os.path.dirname(pPath)
sys.path.append(pPath)
print(pPath)


if __name__ == '__main__':
    os.system("del /s /q /f report\\*.txt")
    os.system("del /s /q /f report\\*.xml")
    pytest.main(['-s', 'testcases/', '-k', 'not Timeout', '--alluredir', 'report'])
