#!/usr/bin/env python3
# -*-coding:utf-8-*-

import json
import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.MqttClient import *
from utils.IFFunctions import *


@allure.feature("scenario")
class TestContinueOrderSingleSKU(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("初始化HTTP客户端。"):
                cls.sv_protocol = cls.config.getItem('server', 'protocol')
                cls.sv_host = cls.config.getItem('server', 'host')
                cls.sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(cls.sv_protocol, cls.sv_host, cls.sv_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)
            with allure.step("初始化数据库连接。"):
                db_user = cls.config.getItem('db', 'db_user')
                db_password = cls.config.getItem('db', 'db_password')
                db_host = cls.config.getItem('db', 'db_host')
                db_database = cls.config.getItem('db', 'db_database')
                db_port = int(cls.config.getItem('db', 'db_port'))
                allure.attach("db_params",
                              "{0}, {1}, {2}, {3}, {4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)

            with allure.step("初始化MQTT客户端"):
                cls.devicename = cls.config.getItem('device', 'd1_devicename')
                cls.secret = cls.config.getItem('device', 'd1_secret')
                cls.productkey = cls.config.getItem('device', 'd1_productkey')
                cls.order_create = cls.config.getItem('iot', 'ServiceOrderPush')
                cls.order_close = cls.config.getItem('iot', 'ServiceOrderClose')
                allure.attach("device params", str((cls.devicename, cls.secret, cls.productkey)))
                cls.logger.info("device params: {}".format((cls.devicename, cls.secret, cls.productkey)))
                params = AliParam(ProductKey=cls.productkey, DeviceName=cls.devicename,
                                  DeviceSecret=cls.secret)
                clientid, username, password, hostname = params.get_param()
                cls.mqttclient = MqttClient(hostname, clientid, username, password)
            with allure.step("初始化MQTT客户端2"):
                cls.devicename2 = cls.config.getItem('device', 'd2_devicename')
                cls.secret2 = cls.config.getItem('device', 'd2_secret')
                cls.productkey2 = cls.config.getItem('device', 'd2_productkey')
                allure.attach("device params", str((cls.devicename2, cls.secret2, cls.productkey2)))
                cls.logger.info("device params: {}".format((cls.devicename2, cls.secret2, cls.productkey2)))
                params2 = AliParam(ProductKey=cls.productkey2, DeviceName=cls.devicename2,
                                  DeviceSecret=cls.secret2)
                clientid2, username2, password2, hostname2 = params2.get_param()
                cls.mqttclient2 = MqttClient(hostname2, clientid2, username2, password2)

            with allure.step("delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                cls.logger.info("table: {0}".format(table))
                delete_result = cls.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                cls.logger.info("delete result: {0}".format(delete_result))
        except Exception as e:
            cls.logger.error("Error: there is exception occur:")
            cls.logger.error(e)
            assert False
        finally:
            cls.logger.info("*** End setup class ***")
            cls.logger.info("")

    @allure.step("+++ teardown class +++")
    def teardown_class(cls):
        cls.logger.info("")
        cls.logger.info("*** Start teardown class ***")
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        if hasattr(cls, 'mqttclient'):
            cls.mqttclient.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")