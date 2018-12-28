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


@pytest.mark.IOT
@allure.feature("IOT-设备错误上报")
class TestDeviceErrorReport(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()
        cls.logger.info("")
        cls.logger.info("*** The setup class method.")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("初始化MQTT客户端"):
                # 读取配置文件，获取IOT服务端所需参数
                cls.ProductKey = cls.config.getItem("device", "d3_productkey")
                cls.DeviceName = cls.config.getItem("device", "d3_devicename")
                cls.DeviceSecret = cls.config.getItem("device", "d3_secret")
                cls.device_id = cls.DeviceName[cls.DeviceName.rfind("_")+1:]
                cls.error_report = cls.config.getItem("iot", "Error")
                cls.params = AliParam(ProductKey=cls.ProductKey, DeviceName=cls.DeviceName,
                                      DeviceSecret=cls.DeviceSecret)
                cls.clientid, cls.username, cls.password, cls.hostname = cls.params.get_param()
                allure.attach("mqtt_params",
                              "{0}, {1}, {2}, {3}".format(cls.clientid, cls.username,cls.password, cls.hostname))
                cls.logger.info(
                    "client_id: {0}, username: {1}, password: {2}, hostname: {3}".format(cls.clientid, cls.username,
                                                                                         cls.password, cls.hostname))
                cls.mqtt_client = MqttClient(host=cls.hostname, client_id=cls.clientid, username=cls.username,
                                             password=cls.password)
            with allure.step("初始化数据库连接"):
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
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        with allure.step("delete device error log"):
            table = 'bus_device_log'
            condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_conditions(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        with allure.step("delete device error log"):
            table = 'bus_device_log'
            condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_conditions(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("设备错误上报")
    @allure.testcase("FT-HTJK-003-082")
    def test_003082_device_error_report(self):
        self.logger.info(".... test_003082_device_error_report ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                 "data": {
                                     "device_id": self.device_id,
                                     "error_info": "123456_error"},
                                 "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                start_time = datetime.datetime.now()
                while not query_result:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = end_time - start_time
                    if during.seconds > 60:
                        self.logger.error("no device error log!")
                        assert False
                    query_result = self.mysql.execute_select_conditions(table, condition)
                device_error_log = query_result[0]
                allure.attach("device_error_log", str(device_error_log))
                self.logger.info("device_error_log:{0}".format(device_error_log))
            with allure.step("teststep4:assert device error log."):
                device_id_in_error_log = device_error_log[2]
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:",str(device_id_in_error_log))
                self.logger.info("Actual device id:{0}".format(device_id_in_error_log))
                log_content = device_error_log[5]
                allure.attach("Expect log content:", str(send_payload))
                allure.attach("Actual log content:", str(log_content))
                self.logger.info("Actual log content:{0}".format(log_content))
                assert self.device_id == str(device_id_in_error_log)
                assert str(send_payload) == log_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003082_device_error_report ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload设置错误的action_id,设备错误上报")
    @allure.testcase("FT-HTJK-003-083")
    @pytest.mark.parametrize("action_id, result",
                             [('109', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []), ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["action_id(非100)", "action_id(超长值)", "action_id(小数)", "action_id(中文)",
                                  "action_id(字母)", "action_id(特殊字符)", "action_id(数字字母)", "action_id(数字中文)",
                                  "action_id(数字特殊字符)", "action_id(空格)", "action_id(空)"])
    def test_003083_device_error_report_incorrect_action_id(self, action_id, result):
        self.logger.info(".... test_003083_device_error_report_incorrect_action_id ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": action_id,
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": "123456_error"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = ("log_type", "error")
                query_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003083_device_error_report_incorrect_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload设置错误的device_id,设备错误上报")
    @allure.testcase("FT-HTJK-003-084")
    @pytest.mark.parametrize("device_id, result",
                             [('33912662580592640', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []),
                              ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["device_id(非增加设备id值)", "device_id(超长值)", "device_id(小数)", "device_id(中文)",
                                  "device_id(字母)", "device_id(特殊字符)", "device_id(数字字母)", "device_id(数字中文)",
                                  "device_id(数字特殊字符)", "device_id(空格)", "device_id(空)"])
    def test_003084_device_error_report_incorrect_device_id(self, device_id, result):
        self.logger.info(".... test_003084_device_error_report_incorrect_device_id ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": device_id,
                                    "error_info": "123456_error"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003084_device_error_report_incorrect_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正确error_info,设备错误上报")
    @allure.testcase("FT-HTJK-003-085")
    @pytest.mark.parametrize("error_info",
                             [('1'), ('10000' * 100), ('1.5'), ('中'), ('a'), ('*'), ('1A'),
                              ('1中'), ('1*')],
                             ids=["error_info(最少长度)", "error_info(最大长度)", "error_info(小数)", "error_info(中文)",
                                  "error_info(字母)", "error_info(特殊字符)", "error_info(数字字母)", "error_info(数字中文)",
                                  "error_info(数字特殊字符)"])
    def test_003085_device_error_report_correct_error_info(self, error_info):
        self.logger.info(".... test_003085_device_error_report_correct_error_info ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": error_info},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                start_time = datetime.datetime.now()
                while not query_result:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = end_time - start_time
                    if during.seconds > 60:
                        self.logger.error("no device error log!")
                        assert False
                    query_result = self.mysql.execute_select_conditions(table, condition)
                device_error_log = query_result[0]
                allure.attach("device_error_log", str(device_error_log))
                self.logger.info("device_error_log:{0}".format(device_error_log))
            with allure.step("teststep4:assert device error log."):
                device_id_in_error_log = device_error_log[2]
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:", str(device_id_in_error_log))
                self.logger.info("Actual device id:{0}".format(device_id_in_error_log))
                log_content = device_error_log[5]
                allure.attach("Expect log content:", str(send_payload))
                allure.attach("Actual log content:", str(log_content))
                self.logger.info("Actual log content:{0}".format(log_content))
                assert self.device_id == str(device_id_in_error_log)
                assert str(send_payload) == log_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003085_device_error_report_correct_error_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload设置错误的error_info,设备错误上报")
    @allure.testcase("FT-HTJK-003-086")
    @pytest.mark.parametrize("error_info, result",
                             [('1'*600, []), (' ', []), ('', [])],
                             ids=["error_info(超长值)", "error_info(空格)", "error_info(空)"])
    def test_003086_device_error_report_incorrect_error_info(self, error_info, result):
        self.logger.info(".... test_003087_device_error_report_incorrect_error_info ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": error_info},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003086_device_error_report_incorrect_error_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正确timestamp,设备错误上报")
    @allure.testcase("FT-HTJK-003-087")
    @pytest.mark.parametrize("timestamp",
                             [(1), (9999999999)],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_003087_device_error_report_correct_timestamp(self, timestamp):
        self.logger.info(".... test_003087_device_error_report_correct_timestamp ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": "123456_error"},
                                "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                start_time = datetime.datetime.now()
                while not query_result:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = end_time - start_time
                    if during.seconds > 60:
                        self.logger.error("no device error log!")
                        assert False
                    query_result = self.mysql.execute_select_conditions(table, condition)
                device_error_log = query_result[0]
                allure.attach("device_error_log", str(device_error_log))
                self.logger.info("device_error_log:{0}".format(device_error_log))
            with allure.step("teststep4:assert device error log."):
                device_id_in_error_log = device_error_log[2]
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:", str(device_id_in_error_log))
                self.logger.info("Actual device id:{0}".format(device_id_in_error_log))
                log_content = device_error_log[5]
                allure.attach("Expect log content:", str(send_payload))
                allure.attach("Actual log content:", str(log_content))
                self.logger.info("Actual log content:{0}".format(log_content))
                assert self.device_id == str(device_id_in_error_log)
                assert str(send_payload) == log_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003087_device_error_report_correct_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload设置错误的timestamp,设备错误上报")
    @allure.testcase("FT-HTJK-003-088")
    @pytest.mark.parametrize("timestamp, result",
                             [(9223372036854775807, []), (0, []), (-1, []), (-9223372036854775809, []),
                              (9223372036854775808, []), (1.5, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_003088_device_error_report_incorrect_timestamp(self, timestamp, result):
        self.logger.info(".... test_003088_device_error_report_incorrect_timestamp ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": "123456_error"},
                                "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003088_device_error_report_incorrect_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload缺少action_id,设备错误上报")
    @allure.testcase("FT-HTJK-003-089")
    def test_003089_device_error_report_no_action_id(self):
        self.logger.info(".... test_003089_device_error_report_no_action_id ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {
                                "data": {
                                    "device_id": self.device_id,
                                    "error_info": "123456_error"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003089_device_error_report_no_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload缺少device_id,设备错误上报")
    @allure.testcase("FT-HTJK-003-090")
    def test_003090_device_error_report_no_device_id(self):
        self.logger.info(".... test_003090_device_error_report_no_device_id ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "error_info": "123456_error"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003090_device_error_report_no_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload缺少error_info,设备错误上报")
    @allure.testcase("FT-HTJK-003-091")
    def test_003091_device_error_report_no_error_info(self):
        self.logger.info(".... test_003091_device_error_report_no_error_info ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003091_device_error_report_no_error_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("payload缺少timestamp,设备错误上报")
    @allure.testcase("FT-HTJK-003-092")
    def test_003092_device_error_report_no_timestamp(self):
        self.logger.info(".... test_003092_device_error_report_no_timestamp ....")
        topic = "/{0}/{1}/{2}".format(self.ProductKey, self.DeviceName, self.error_report)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report device error"):
                self.logger.info("report device error.")
                send_payload = {"action_id": "102",
                                "data": {
                                    "device_id": self.device_id,
                                "error_info": "123456_error"}}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report device error. ")
            with allure.step("teststep3:get device error log from db."):
                time.sleep(10)
                table = "bus_device_log"
                condition = "log_type like '%error%' and device_id = {0}".format(self.device_id)
                query_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("device_error_log", str(query_result))
                self.logger.info("device_error_log:{0}".format(query_result))
            with allure.step("teststep4:assert device error log."):
                allure.attach("Expect count of error log:", "0")
                allure.attach("Actual count of error log:", str(len(query_result)))
                self.logger.info("Actual count of error log:{0}".format(len(query_result)))
                assert query_result == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003092_device_error_report_no_timestamp ....")
            self.logger.info("")

if __name__ == '__main__':
    # pytest.main(['-s', 'test_IOT_Device_Error_Report.py'])
    pytest.main(['-s', 'test_IOT_Device_Error_Report.py::TestDeviceErrorReport::test_003082_device_error_report'])
