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


@allure.feature("IOT-服务单状态（设备上报）")
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
                cls.device_id = cls.DeviceName[cls.DeviceName.rfind("_") + 1:]
                cls.params = AliParam(ProductKey=cls.ProductKey, DeviceName=cls.DeviceName,
                                      DeviceSecret=cls.DeviceSecret)
                cls.clientid, cls.username, cls.password, cls.hostname = cls.params.get_param()
                allure.attach("mqtt_params",
                              "{0}, {1}, {2}, {3}".format(cls.clientid, cls.username, cls.password, cls.hostname))
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
            with allure.step("get provider id"):
                provider_name = cls.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.provider_id = select_result[0][0]
            with allure.step("get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", cls.provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.spu_id = select_result[0][0]
            with allure.step("get sku id"):
                sku_name = cls.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.sku_id = select_result[0][0]
            with allure.step("初始化HTTP客户端2。"):
                h5_port = cls.config.getItem('h5', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, h5_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient2 = HTTPClient(baseurl)
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
        if hasattr(cls, 'httpclient2'):
            cls.httpclient2.close()
        if hasattr(cls, "mysql"):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        with allure.step("注册用户，生成member_id"):
            code_type = 2
            client_type = 2
            client_version = "v1"
            device_token = "138001380001234"
            imei = "138001380001234"
            phone = "13800138000"
            sms_code = "123456"
            login_result = make_login(self.httpclient, code_type, client_type, client_version, device_token, imei,
                                      phone, sms_code, logger=self.logger)
            if login_result == {}:
                self.logger.error("user login failed!")
                assert False
            self.member_id = login_result["user_info"]["member_id"]
            self.token = login_result['token']
        with allure.step("进行身份认证，获取feature_id"):
            headers = {"authorization": self.token}
            identity_card_face = "fore2.jpg"
            identity_card_emblem = "back2.jpg"
            face_picture = "face2.jpg"
            self.httpclient.update_header(headers)
            identity_myfeature = user_myfeature(self.httpclient, self.member_id, face_picture, logger=self.logger)
            if not identity_myfeature:
                self.logger.error("identity myfeature failed!")
                assert False
            user_identity_result = user_identity(self.httpclient, self.member_id, identity_card_face,
                                                 identity_card_emblem,
                                                 logger=self.logger)
            if not user_identity_result:
                self.logger.error("user identity failed!")
                assert False
            table_name = "mem_features"
            condition = ("member_id", self.member_id)
            self.features_id = self.mysql.execute_select_condition(table_name, condition)[0][0]
        with allure.step("创建服务单"):
            with allure.step("连接H5主页"):
                r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                allure.attach("homeindex", str(r_homeindex))
                self.logger.info("homeindex: " + str(r_homeindex))
                assert not r_homeindex
            start_time = datetime.datetime.strptime("2018-11-29 00:00:00", "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime("2019-11-28 23:59:59", "%Y-%m-%d %H:%M:%S")
            r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, self.sku_id,
                                                      [self.features_id], start_time, end_time, self.logger)
            allure.attach("apply result", str(r_applyresult1))
            self.logger.info("apply result: " + str(r_applyresult1))
            assert r_applyresult1
        with allure.step("get service order id"):
            table = 'bus_service_order'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("")
            self.logger.info("table: {0}, condition: {1}".format(table, condition))
            select_result = self.mysql.execute_select_condition(table, condition)
            allure.attach("query result", str(select_result))
            self.logger.info("query result: {0}".format(select_result))
            if select_result:
                self.service_order_id = select_result[0][0]
                allure.attach("service order id", str(self.service_order_id))
                self.logger.info("service order id:{0}".format(str(self.service_order_id)))
            else:
                self.logger.info("can not get service order id.")
                assert False
        with allure.step("get business order id"):
            table = 'bus_order'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("")
            self.logger.info("table: {0}, condition: {1}".format(table, condition))
            select_result = self.mysql.execute_select_condition(table, condition)
            allure.attach("query result", str(select_result))
            self.logger.info("query result: {0}".format(select_result))
            if select_result:
                self.bus_order_id = select_result[0][0]
                allure.attach("business order id", str(self.bus_order_id))
                self.logger.info("service order id:{0}".format(str(self.bus_order_id)))
            else:
                self.logger.info("can not get business order id.")
                assert False
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        with allure.step("delete member order record"):
            table = 'mem_order_record'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete service order"):
            table = 'bus_service_order'
            condition = ("member_id", self.member_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete business order"):
            table = 'bus_order'
            condition = ("member_id", self.member_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete bus_service_order_device_list"):
            bus_service_order_device_list_table = "bus_service_order_device_list"
            bus_service_order_device_list_condition = ("device_id", self.device_id)
            allure.attach("table name", str(bus_service_order_device_list_table))
            self.logger.info("table: {0}".format(bus_service_order_device_list_table))
            bus_service_order_device_list_result = self.mysql.execute_delete_condition(
                bus_service_order_device_list_table, bus_service_order_device_list_condition)
            allure.attach("delete result", str(bus_service_order_device_list_result))
            self.logger.info("delete result: {0}".format(bus_service_order_device_list_result))
        with allure.step("delete bus_order_features"):
            table = 'bus_order_features'
            condition = ("service_orderid", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete bus_service_order_status"):
            table = 'bus_service_order_status'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete feature"):
            features_table = "mem_features"
            features_condition = ("features_id", self.features_id)
            allure.attach("table name", str(features_table))
            self.logger.info("table: {0}".format(features_table))
            features_delete_result = self.mysql.execute_delete_condition(features_table, features_condition)
            allure.attach("delete result", str(features_delete_result))
            self.logger.info("delete result: {0}".format(features_delete_result))
        with allure.step("delete member"):
            member_table = "mem_member"
            mem_condition = ("member_id", self.member_id)
            allure.attach("table name", str(member_table))
            self.logger.info("table: {0}".format(member_table))
            mem_delete_result = self.mysql.execute_delete_condition(member_table, mem_condition)
            allure.attach("delete result", str(mem_delete_result))
            self.logger.info("delete result: {0}".format(mem_delete_result))
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
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                time_stamp = get_timestamp()
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": in_out,
                                         "exrea": ""}, "timestamp": str(time_stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get recognized record failed.")
                    assert False
                record_list = recognize_record["data"]
                start_time = datetime.datetime.now()
                while record_list == []:
                    time.sleep(5)
                    recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                                  logger=self.logger)
                    if recognize_record == {}:
                        self.logger.error("get service order records failed.")
                        assert False
                    record_list = recognize_record["data"]
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("business system has not receive the service order report")
                        assert False
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                record = record_list[0]
                device_id_in_record = record["device_id"]
                service_order_id_in_record = record["service_order_id"]
                check_time = record["check_time"]
                in_out_in_record = record["in_out"]
            with allure.step("teststep4:assert the record."):
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:", str(device_id_in_record))
                self.logger.info("Actual device id:{0}".format(device_id_in_record))
                allure.attach("Expect service order id:", str(self.service_order_id))
                allure.attach("Actual service order id:", str(service_order_id_in_record))
                self.logger.info("Actual service order id:{0}".format(service_order_id_in_record))
                allure.attach("Expect in_out:", str(in_out))
                allure.attach("Actual in_out:", str(in_out_in_record))
                self.logger.info("Actual in_out:{0}".format(in_out_in_record))
                allure.attach("Expect timestamp:", str(time_stamp))
                allure.attach("Actual timestamp:", str(check_time))
                self.logger.info("Actual timestamp:{0}".format(check_time))
                allure.attach("Actual already_count:", str(already_count))
                self.logger.info("Actual already_count:{0}".format(already_count))
                assert str(device_id_in_record) == str(self.device_id)
                assert str(service_order_id_in_record) == str(self.service_order_id)
                assert int(in_out) == in_out_in_record
                assert time_stamp == check_time
                assert already_count > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003054_report_service_order_status ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误action id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-55")
    @pytest.mark.parametrize("action_id, result",
                             [('109', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []), ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["action_id(非100)", "action_id(超长值)", "action_id(小数)", "action_id(中文)",
                                  "action_id(字母)", "action_id(特殊字符)", "action_id(数字字母)", "action_id(数字中文)",
                                  "action_id(数字特殊字符)", "action_id(空格)", "action_id(空)"])
    def test_003055_report_service_order_status_incorrect_action_id(self, action_id, result):
        self.logger.info(".... test_003055_report_service_order_status_incorrect_action_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": action_id,
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str(result))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == result
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003055_report_service_order_status_incorrect_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误service_order_id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-56")
    @pytest.mark.parametrize("service_order_id",
                             [('26171582619975681'), ('100' * 10), ('1.5'), ('中'), ('a'), ('*'),
                              ('1A'), ('1中'), ('1*'), (' '), ('')],
                             ids=["service_order_id(非增加服务单值)", "service_order_id(超长值)", "service_order_id(小数)",
                                  "service_order_id(中文)", "service_order_id(字母)",
                                  "service_order_id(特殊字符)", "service_order_id(数字字母)", "service_order_id(数字中文)",
                                  "service_order_id(数字特殊字符)", "service_order_id(空格)", "service_order_id(空)"])
    def test_003056_report_service_order_status_incorrect_service_order_id(self, service_order_id):
        self.logger.info(".... test_003056_report_service_order_status_incorrect_service_order_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2: get the count of records from db before report service order status"):
                table_name = "mem_order_record"
                condition = ("device_id", self.device_id)
                count_of_records_before_report = len(self.mysql.execute_select_condition(table_name, condition))
                allure.attach("count_of_records_before_report", str(count_of_records_before_report))
                self.logger.info("count_of_records_before_report:{0}".format(count_of_records_before_report))
            with allure.step("teststep3:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": service_order_id,
                                         "device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep4:get the count of records from db after report service order status."):
                time.sleep(5)
                count_of_records_after_report = len(self.mysql.execute_select_condition(table_name, condition))
                allure.attach("count_of_records_after_report", str(count_of_records_after_report))
                self.logger.info("count_of_records_after_report:{0}".format(count_of_records_after_report))
            with allure.step("teststep5:assert the counts."):
                allure.attach("Expect count_of_records_after_report == count_of_records_before_report:", str(True))
                allure.attach("Actual count_of_records_after_report == count_of_records_before_report:",
                              str(count_of_records_after_report == count_of_records_before_report))
                self.logger.info("Actual count_of_records_after_report == count_of_records_before_report:{0}".format(
                    count_of_records_after_report == count_of_records_before_report))
                assert count_of_records_after_report == count_of_records_before_report
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003056_report_service_order_status_incorrect_service_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误device id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-57")
    @pytest.mark.parametrize("device_id, result",
                             [('33912662580592640', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []),
                              ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["device_id(非增加设备id值)", "device_id(超长值)", "device_id(小数)", "device_id(中文)",
                                  "device_id(字母)", "device_id(特殊字符)", "device_id(数字字母)", "device_id(数字中文)",
                                  "device_id(数字特殊字符)", "device_id(空格)", "device_id(空)"])
    def test_003057_report_service_order_status_incorrect_device_id(self, device_id, result):
        self.logger.info(".... test_003057_report_service_order_status_incorrect_device_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str(result))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == result
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003057_report_service_order_status_incorrect_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误in_out,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-58")
    @pytest.mark.parametrize("in_out, result",
                             [('200', []), ('-200', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []),
                              ('1A', []), ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["in_out(非0、1、-1)", "in_out(非0、1、-1)_2", "in_out(超长值)", "in_out(小数)",
                                  "in_out(中文)", "in_out(字母)", "in_out(特殊字符)", "in_out(数字字母)",
                                  "in_out(数字中文)", "in_out(数字特殊字符)", "in_out(空格)", "in_out(空)"])
    def test_003058_report_service_order_status_incorrect_in_out(self, in_out, result):
        self.logger.info(".... test_003058_report_service_order_status_incorrect_in_out ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": in_out,
                                         "exrea": ""}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str(result))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == result
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003058_report_service_order_status_incorrect_in_out ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确exrea值，正常设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-59")
    @pytest.mark.parametrize("exrea",
                             [(''), ('{"action_id":123,"data":"abc","timestamp":123456}'),
                              ('{"action_id":123,"data":{"sub":"abc","sub2":123},"timestamp":123456}')],
                             ids=["exrea(空值)", "exrea(JSON格式数据)_1", "exrea(JSON格式数据)_2"])
    def test_003059_report_service_order_status_correct_exrea(self, exrea):
        self.logger.info(".... test_003059_report_service_order_status_correct_exrea ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                time_stamp = get_timestamp()
                in_out = 1
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": in_out,
                                         "exrea": exrea}, "timestamp": str(time_stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get recognized record failed.")
                    assert False
                record_list = recognize_record["data"]
                start_time = datetime.datetime.now()
                while record_list == []:
                    time.sleep(5)
                    recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                                  logger=self.logger)
                    if recognize_record == {}:
                        self.logger.error("get service order records failed.")
                        assert False
                    record_list = recognize_record["data"]
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("business system has not receive the service order report")
                        assert False
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                record = record_list[0]
                device_id_in_record = record["device_id"]
                service_order_id_in_record = record["service_order_id"]
                check_time = record["check_time"]
                in_out_in_record = record["in_out"]
            with allure.step("teststep4:assert the record."):
                table = 'mem_order_record'
                condition = ("service_order_id", self.service_order_id)
                select_result = self.mysql.execute_select_condition(table, condition)
                if not select_result:
                    self.logger.error("no record!")
                    assert False
                report_content = select_result[0][6]
                allure.attach("Expect report_content:", str(send_payload))
                allure.attach("Actual report_content:", str(report_content))
                self.logger.info("Actual report_content:{0}".format(report_content))
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:", str(device_id_in_record))
                self.logger.info("Actual device id:{0}".format(device_id_in_record))
                allure.attach("Expect service order id:", str(self.service_order_id))
                allure.attach("Actual service order id:", str(service_order_id_in_record))
                self.logger.info("Actual service order id:{0}".format(service_order_id_in_record))
                allure.attach("Expect in_out:", str(in_out))
                allure.attach("Actual in_out:", str(in_out_in_record))
                self.logger.info("Actual in_out:{0}".format(in_out_in_record))
                allure.attach("Expect timestamp:", str(time_stamp))
                allure.attach("Actual timestamp:", str(check_time))
                self.logger.info("Actual timestamp:{0}".format(check_time))
                allure.attach("Actual already_count:", str(already_count))
                self.logger.info("Actual already_count:{0}".format(already_count))
                assert report_content == str(send_payload)
                assert str(device_id_in_record) == str(self.device_id)
                assert str(service_order_id_in_record) == str(self.service_order_id)
                assert int(in_out) == in_out_in_record
                assert time_stamp == check_time
                assert already_count > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003059_report_service_order_status_correct_exrea ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误exrea,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-60")
    @pytest.mark.parametrize("exrea, result",
                             [('{123}', []), ('100' * 10, []), (1.5, []), ('中', []), ('a', []), ('*', []),
                              ('1A', []), ('1中', []), ('1*', []), (' ', [])],
                             ids=["exrea(非JSON格式数据)", "exrea(超长值)", "exrea(小数)",
                                  "exrea(中文)", "exrea(字母)", "exrea(特殊字符)", "exrea(数字字母)",
                                  "exrea(数字中文)", "exrea(数字特殊字符)", "exrea(空格)"])
    def test_003060_report_service_order_status_incorrect_exrea(self, exrea, result):
        self.logger.info(".... test_003060_report_service_order_status_incorrect_exrea ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": exrea}, "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str(result))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == result
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003060_report_service_order_status_incorrect_exrea ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值，正常设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-61")
    @pytest.mark.parametrize("timestamp",
                             [(1), (9999999999)],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_003061_report_service_order_status_correct_timestamp(self, timestamp):
        self.logger.info(".... test_003061_report_service_order_status_correct_timestamp ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                in_out = 1
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": in_out,
                                         "exrea": ""}, "timestamp": timestamp}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get recognized record failed.")
                    assert False
                record_list = recognize_record["data"]
                start_time = datetime.datetime.now()
                while record_list == []:
                    time.sleep(5)
                    recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                                  logger=self.logger)
                    if recognize_record == {}:
                        self.logger.error("get service order records failed.")
                        assert False
                    record_list = recognize_record["data"]
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("business system has not receive the service order report")
                        assert False
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                record = record_list[0]
                device_id_in_record = record["device_id"]
                service_order_id_in_record = record["service_order_id"]
                check_time = record["check_time"]
                in_out_in_record = record["in_out"]
            with allure.step("teststep4:assert the record."):
                allure.attach("Expect device id:", str(self.device_id))
                allure.attach("Actual device id:", str(device_id_in_record))
                self.logger.info("Actual device id:{0}".format(device_id_in_record))
                allure.attach("Expect service order id:", str(self.service_order_id))
                allure.attach("Actual service order id:", str(service_order_id_in_record))
                self.logger.info("Actual service order id:{0}".format(service_order_id_in_record))
                allure.attach("Expect in_out:", str(in_out))
                allure.attach("Actual in_out:", str(in_out_in_record))
                self.logger.info("Actual in_out:{0}".format(in_out_in_record))
                allure.attach("Expect timestamp:", str(timestamp))
                allure.attach("Actual timestamp:", str(check_time))
                self.logger.info("Actual timestamp:{0}".format(check_time))
                allure.attach("Actual already_count:", str(already_count))
                self.logger.info("Actual already_count:{0}".format(already_count))
                assert str(device_id_in_record) == str(self.device_id)
                assert str(service_order_id_in_record) == str(self.service_order_id)
                assert int(in_out) == in_out_in_record
                assert timestamp == check_time
                assert already_count > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003061_report_service_order_status_correct_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误timestamp,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-062")
    @pytest.mark.parametrize("timestamp, result",
                             [(9223372036854775807, []), (0, []), (-1, []), (-9223372036854775809, []),
                              (9223372036854775808, []), (1.5, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_003062_report_service_order_status_incorrect_timestamp(self, timestamp, result):
        self.logger.info(".... test_003062_report_service_order_status_incorrect_timestamp ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": timestamp}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str(result))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == result
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003062_report_service_order_status_incorrect_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少action_id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-063")
    def test_003063_report_service_order_status_no_action_id(self):
        self.logger.info(".... test_003063_report_service_order_status_no_action_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"data": {"service_order_id": str(self.service_order_id),
                                         "device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": get_timestamp()}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str([]))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == []
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003063_report_service_order_status_no_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少service_order_id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-064")
    def test_003064_report_service_order_status_no_service_order_id(self):
        self.logger.info(".... test_003064_report_service_order_status_no_service_order_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2: get the count of records from db before report service order status"):
                table_name = "mem_order_record"
                condition = ("device_id", self.device_id)
                count_of_records_before_report = len(self.mysql.execute_select_condition(table_name, condition))
                allure.attach("count_of_records_before_report", str(count_of_records_before_report))
                self.logger.info("count_of_records_before_report:{0}".format(count_of_records_before_report))
            with allure.step("teststep3:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"device_id": self.device_id,
                                         "in_out": 1,
                                         "exrea": ""}, "timestamp": get_timestamp()}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep4:get the count of records from db after report service order status."):
                time.sleep(5)
                count_of_records_after_report = len(self.mysql.execute_select_condition(table_name, condition))
                allure.attach("count_of_records_after_report", str(count_of_records_after_report))
                self.logger.info("count_of_records_after_report:{0}".format(count_of_records_after_report))
            with allure.step("teststep5:assert the counts."):
                allure.attach("Expect count_of_records_after_report == count_of_records_before_report:", str(True))
                allure.attach("Actual count_of_records_after_report == count_of_records_before_report:",
                              str(count_of_records_after_report == count_of_records_before_report))
                self.logger.info("Actual count_of_records_after_report == count_of_records_before_report:{0}".format(
                    count_of_records_after_report == count_of_records_before_report))
                assert count_of_records_after_report == count_of_records_before_report
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003064_report_service_order_status_no_service_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_id,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-065")
    def test_003065_report_service_order_status_no_device_id(self):
        self.logger.info(".... test_003065_report_service_order_status_no_device_id ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"service_order_id": str(self.service_order_id),
                                         "in_out": 1,
                                         "exrea": ""},
                                "timestamp": get_timestamp()}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str([]))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == []
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003065_report_service_order_status_no_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少exrea,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-066")
    def test_003066_report_service_order_status_no_exrea(self):
        self.logger.info(".... test_003066_report_service_order_status_no_exrea ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"device_id": self.device_id,
                                         "service_order_id": str(self.service_order_id),
                                         "in_out": 1,
                                         },
                                "timestamp": get_timestamp()}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str([]))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == []
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003066_report_service_order_status_no_exrea ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp,设备上报服务单状态")
    @allure.testcase("FT-HTJK-003-067")
    def test_003067_report_service_order_status_no_timestamp(self):
        self.logger.info(".... test_003067_report_service_order_status_no_timestamp ....")
        topic = "/{0}/{1}/ServiceOrderReport".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: start mqtt_client."):
                self.mqtt_client.loopstart()
            with allure.step("teststep2:report service order status"):
                self.logger.info("report service order status.")
                send_payload = {"action_id": "100",
                                "data": {"device_id": self.device_id,
                                         "service_order_id": str(self.service_order_id),
                                         "in_out": 1,
                                         "exrea": ""}
                                }
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(topic, str(send_payload), 1)
                self.logger.info("finish report service order status. ")
            with allure.step("teststep3:get service order status from business system."):
                time.sleep(5)
                service_order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3,
                                                              logger=self.logger)
                if service_order_list == []:
                    self.logger.error("get service order list failed.")
                    assert False
                already_count = service_order_list[0]["already_count"]
                self.logger.info("already_count:{0}".format(already_count))
                recognize_record = get_recognized_record_list(self.httpclient, self.member_id, 0, 20,
                                                              logger=self.logger)
                if recognize_record == {}:
                    self.logger.error("get service order records failed.")
                    assert False
                record_list = recognize_record["data"]
            with allure.step("teststep4:assert the service order status."):
                allure.attach("Expect service order status report:", str([]))
                allure.attach("Actual service order status report:", str(record_list))
                self.logger.info("Actual service order status report:{0}".format(record_list))
                assert record_list == []
                assert already_count == 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003067_report_service_order_status_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_IOT_ServiceOrder_Report.py'])
    # pytest.main(['-s',
    #              'test_IOT_ServiceOrder_Report.py::TestServiceOrderReport::test_003066_report_service_order_status_no_exrea'])
