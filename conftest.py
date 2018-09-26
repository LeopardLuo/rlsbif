#!/usr/bin/env python
# -*-coding:utf-8-*-

import os, re
import pytest
import allure
from utils.ConfigParse import ConfigParse

@pytest.fixture(scope="session", autouse=True)
def setupenv(request):
    root_dir = request.config.rootdir
    print(root_dir)
    cp = ConfigParse()
    allure.environment(host=cp.getItem('allure', 'host'))  # 测试报告中展示host
    allure.environment(browser=cp.getItem('allure', 'browser'))  # 测试报告中展示browser
