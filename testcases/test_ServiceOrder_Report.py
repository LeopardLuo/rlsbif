#!/usr/bin/env python3
# -*-coding:utf-8-*-

import pytest
import allure
import random

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *
from utils.MqttClient import *
import json
import datetime


@allure.feature("服务单状态（设备上报）")
class TestServiceOrderReport(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()
        cls.logger.info("")
        cls.logger.info("*** The setup class method.")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("初始化HTTP客户端。"):
                sv_protocol = cls.config.getItem('server', 'protocol')
                sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, sv_port)
                allure.attach("baseurl", "{0}".format(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)
            with allure.step("初始化MQTT客户端"):
                # 读取配置文件，获取IOT服务端所需参数
                cls.ProductKey = cls.config.getItem("device", "d3_productkey")
                cls.DeviceName = cls.config.getItem("device", "d3_devicename")
                cls.DeviceSecret = cls.config.getItem("device", "d3_secret")
                cls.params = AliParam(ProductKey=cls.ProductKey, DeviceName=cls.DeviceName,
                                      DeviceSecret=cls.DeviceSecret)
                cls.clientid, cls.username, cls.password, cls.hostname = cls.params.get_param()
                cls.logger.info(
                    "client_id: {0}, username: {1}, password: {2}, hostname: {3}".format(cls.clientid, cls.username,
                                                                                         cls.password, cls.hostname))
                cls.mqtt_client = MqttClient(host=cls.hostname, client_id=cls.clientid, username=cls.username,
                                             password=cls.password)
        except Exception as e:
            cls.logger.error("Error: there is exception occur:")
            cls.logger.error(e)
            assert False
        cls.logger.info("*** End setup class ***")
        cls.logger.info("")

    @allure.step("+++ teardown class +++")
    def teardown_class(cls):
        cls.logger.info("")
        cls.logger.info("*** Start teardown class ***")
        if hasattr(cls, 'mqtt_client'):
            cls.mqtt_client.close()
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        with allure.step("初始化数据库连接"):
            db_user = self.config.getItem('db', 'db_user')
            db_password = self.config.getItem('db', 'db_password')
            db_host = self.config.getItem('db', 'db_host')
            db_database = self.config.getItem('db', 'db_database')
            db_port = int(self.config.getItem('db', 'db_port'))
            allure.attach("db_params",
                          "{0}, {1}, {2}, {3}, {4}".format(db_user, db_password, db_host, db_database, db_port))
            self.logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                             "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
            self.mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)
        with allure.step("创建服务单"):
            self.logger.info("strat to create service order.")
            self.system_id = "15596785737138176"
            random_num = ""
            # 生成随机4位数
            for i in range(4):
                ch = chr(random.randrange(ord('0'), ord('9') + 1))
                random_num += ch
            business_order_id = str(get_timestamp()) + random_num
            self.system_code = "ba80b269044e7501d1b4e7890d319ff5"
            member_id = 23834536681144320
            features_id = 23854189239205888
            service_unit = "慧睿思通AI产品部4"
            service_address = "广州番禺区北大街"
            begin_time = get_timestamp() + 300
            end_time = 9999999999
            in_count = 10
            verify_condition_type = 2
            device_ids = ["23912662580592640"]
            create_service_order_result = h5_create_service_order(self.httpclient, self.system_id, business_order_id,
                                                                 member_id, self.system_code, features_id, device_ids,
                                                                 verify_condition_type, begin_time, end_time,
                                                                 in_count, service_unit, service_address,
                                                                 logger=self.logger)
            if create_service_order_result:
                self.service_order_id = create_service_order_result["service_order_id"]
                self.logger.info("service order id:" + str(self.service_order_id))
            else:
                self.logger.info("create service order failed.")
                assert False
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        with allure.step("delete service order"):
            table = 'bus_service_order'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete bus service order status"):
            table = 'bus_service_order_status'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete member order record"):
            table = 'mem_order_record'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        if hasattr(self, "mysql"):
            self.mysql.close()
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("正常设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-54")
    @pytest.mark.parametrize("in_out",
                             [('0'), ('1'), ('-1')],
                             ids=["in_out(进)", "in_out(出)", "in_out(未知)"])
    def test_003054_report_service_order_status(self, in_out):
        self.logger.info(".... test_003054_report_service_order_status ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": "23912662580592640",
                                         "in_out": in_out,
                                         "exrea": ""}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_records = bs_get_service_order_records(self.httpclient, self.system_id,
                                                                     self.service_order_id, self.system_code, 0, 20,
                                                                     get_timestamp(), self.logger)
                record_list = service_order_records["data"]
                start_time = datetime.datetime.now()
                while record_list == []:
                    time.sleep(5)
                    service_order_records = bs_get_service_order_records(self.httpclient, self.system_id,
                                                                         self.service_order_id, self.system_code, 0, 20,
                                                                         get_timestamp(), self.logger)
                    record_list = service_order_records["data"]
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("business system has not receive the service order report")
                        assert False
                allure.attach("service order records content", service_order_records)
                self.logger.info("service order records content:{0}".format(service_order_records))
                service_order_status = bs_get_service_order_status(self.httpclient, self.system_id,
                                                                   self.service_order_id, self.system_code,
                                                                   get_timestamp(), self.logger)
                allure.attach("service order status content", service_order_status)
                self.logger.info("service order status content:{0}".format(service_order_status))
                already_count = service_order_status["already_count"]
            with allure.step("teststep4:assert the service order status."):
                report = record_list[0]["report_content"]
                allure.attach("Expect service order status report:", str(send_payload))
                allure.attach("Actual service order status report:", report)
                self.logger.info("Actual service order status report:{0}".format(report))
                assert str(report) == str(send_payload)
                assert already_count > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... test_003054_report_service_order_status ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_ServiceOrder_Report.py'])

