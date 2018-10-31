#!/usr/bin/env python
# -*-coding:utf-8-*-


import pytest
import allure
from utils.ConfigParse import ConfigParse
from utils.LogTool import Logger


@pytest.fixture(scope="session", autouse=True)
def setupenv(request):
    root_dir = request.config.rootdir
    logger = Logger()
    logger.info("")
    logger.info("                 [**************** Start setupenv **************]")
    logger.info("request.config.rootdir: " + str(root_dir))
    cp = ConfigParse()
    allure.environment(Host=cp.getItem('allure', 'host'))  # 测试报告中展示host
    allure.environment(WebServer=cp.getItem('allure', 'WebServer'))
    allure.environment(Database=cp.getItem('allure', 'database'))
    allure.environment(IDE=cp.getItem('allure', 'IDE'))
    allure.environment(Script=cp.getItem('allure', 'Script'))
    allure.environment(requests=cp.getItem('allure', 'requests'))
    allure.environment(MQTT=cp.getItem('allure', 'MQTT'))

    logger.info("                 [**************** End setupenv **************]")
    logger.info("")
