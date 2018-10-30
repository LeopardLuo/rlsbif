#!/usr/bin/env python
# -*-coding:utf-8-*-


import pytest
import allure
from utils.ConfigParse import ConfigParse
from utils.MysqlClient import MysqlClient
from utils.LogTool import Logger


@pytest.fixture(scope="session", autouse=True)
def setupenv(request):
    root_dir = request.config.rootdir
    logger = Logger()
    logger.info("")
    logger.info("                 [**************** Start setupenv **************]")
    logger.info("request.config.rootdir: " + str(root_dir))

    cp = ConfigParse()
    db_user = cp.getItem('db', 'db_user')
    db_password = cp.getItem('db', 'db_password')
    db_host = cp.getItem('db', 'db_host')
    db_database = cp.getItem('db', 'db_database')
    db_port = int(cp.getItem('db', 'db_port'))
    logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
    mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)
    tables = ['bus_service_order', 'bus_service_order_device_list', 'bus_service_order_status', 'mem_features',
              'mem_member', 'mem_member_identity', 'mem_member_identity_other', 'mem_member_login', 'mem_order_record']
    for table in tables:
        delete_result = mysql.execute_delete_all(table)
        logger.info("delete table ({0}) result: {1}".format(table, delete_result))

    allure.environment(Host=cp.getItem('allure', 'host'))  # 测试报告中展示host
    allure.environment(WebServer=cp.getItem('allure', 'WebServer'))
    allure.environment(Database=cp.getItem('allure', 'database'))
    allure.environment(IDE=cp.getItem('allure', 'IDE'))
    allure.environment(Script=cp.getItem('allure', 'Script'))
    allure.environment(requests=cp.getItem('allure', 'requests'))
    allure.environment(MQTT=cp.getItem('allure', 'MQTT'))

    logger.info("                 [**************** End setupenv **************]")
    logger.info("")
