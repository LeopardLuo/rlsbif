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


@allure.feature("Iot-服务单下发")
class TestServiceOrderPush(object):
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
            with allure.step("teststep: get provider id"):
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
            with allure.step("teststep: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", cls.provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.spu_id = select_result[0][0]
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
            device_token = "1234"*11
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
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
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
        with allure.step("delete member"):
            member_table = "mem_member"
            mem_condition = ("member_id", self.member_id)
            allure.attach("table name", str(member_table))
            self.logger.info("table: {0}".format(member_table))
            mem_delete_result = self.mysql.execute_delete_condition(member_table, mem_condition)
            allure.attach("delete result", str(mem_delete_result))
            self.logger.info("delete result: {0}".format(mem_delete_result))
        with allure.step("delete feature"):
            features_table = "mem_features"
            features_condition = ("features_id", self.features_id)
            allure.attach("table name", str(features_table))
            self.logger.info("table: {0}".format(features_table))
            features_delete_result = self.mysql.execute_delete_condition(features_table, features_condition)
            allure.attach("delete result", str(features_delete_result))
            self.logger.info("delete result: {0}".format(features_delete_result))
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
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的action_id")
    @allure.testcase("FT-HTJK-003-001")
    def test_003001_get_payload_action_id(self):
        self.logger.info(".... test_003001_get_payload_action_id ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        self.logger.info("topic:{0}".format(topic))
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days = 2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the action_id in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                allure.attach("Expect action id:", '201')
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "201"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003001_get_payload_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的服务单流水号")
    @allure.testcase("FT-HTJK-003-002")
    def test_003002_get_payload_service_order_id(self):
        self.logger.info(".... test_003002_get_payload_service_order_id ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the service order id in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                service_order_id_payload = msg_payload_dict["data"]["service_order_id"]
                allure.attach("Expect service order id:", str(self.service_order_id))
                allure.attach("Actual service order id:", str(service_order_id_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual service order id:{0}".format(service_order_id_payload))
                assert service_order_id_payload == str(self.service_order_id)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003002_get_payload_service_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的特征串")
    @allure.testcase("FT-HTJK-003-003")
    def test_003003_get_payload_feature(self):
        self.logger.info(".... test_003003_get_payload_feature ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the feature in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                feature_in_payload = msg_payload_dict["data"]["feature"]
                table_name = "mem_features"
                condition = ("features_id", self.features_id)
                feature = self.mysql.execute_select_condition(table_name, condition)[0][6]
                allure.attach("Expect feature:", str(feature))
                allure.attach("Actual feature:", str(feature_in_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual feature:{0}".format(feature_in_payload))
                assert feature_in_payload == feature
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003003_get_payload_feature ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的特征类型")
    @allure.testcase("FT-HTJK-003-004")
    def test_003004_get_payload_feature_type(self):
        self.logger.info(".... test_003004_get_payload_feature_type ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the feature type in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                feature_type_payload_payload = msg_payload_dict["data"]["feature_type"]
                table_name = "mem_features"
                condition = ("features_id", self.features_id)
                feature_type = self.mysql.execute_select_condition(table_name, condition)[0][4]
                allure.attach("Expect feature type:", str(feature_type))
                allure.attach("Actual feature type:", str(feature_type_payload_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual feature type:{0}".format(feature_type_payload_payload))
                assert feature_type_payload_payload == str(feature_type)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003004_get_payload_feature_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的verify_condition_type")
    @allure.testcase("FT-HTJK-003-005")
    def test_003005_get_payload_verify_condition_type(self):
        self.logger.info(".... test_003005_get_payload_verify_condition_type ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the verify condition type in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                with allure.step("get verify condition type in db"):
                    table = 'bus_sku'
                    condition = ("sku_id", sku_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    verify_condition_type = select_result[0][12]
                allure.attach("Expect verify condition type:", str(verify_condition_type))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert verify_condition_type_payload == str(verify_condition_type)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003005_get_payload_verify_condition_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的begin_time")
    @allure.testcase("FT-HTJK-003-006")
    def test_003006_get_payload_begin_time(self):
        self.logger.info(".... test_003006_get_payload_begin_time ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the begin time in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                begin_time_payload = msg_payload_dict["data"]["begin_time"]
                begin_time = int(time.mktime(time.strptime(start_time, '%Y-%m-%d')))
                allure.attach("Expect begin time:", str(begin_time))
                allure.attach("Actual begin time:", str(begin_time_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time:{0}".format(begin_time_payload))
                assert begin_time_payload == str(begin_time)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003006_get_payload_begin_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的end_time")
    @allure.testcase("FT-HTJK-003-007")
    def test_003007_get_payload_end_time(self):
        self.logger.info(".... test_003007_get_payload_end_time ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the end time in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                end_time_payload = msg_payload_dict["data"]["end_time"]
                end_time_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))
                allure.attach("Expect end time:", str(end_time_stamp))
                allure.attach("Actual end time:", str(end_time_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual end time:{0}".format(end_time_payload))
                assert end_time_payload == str(end_time_stamp)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_003007_get_payload_end_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为1时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-008")
    def test_003008_get_payload_begin_time_and_end_time_1(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_1 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the begin time and end time in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                begin_time_payload = msg_payload_dict["data"]["begin_time"]
                end_time_payload = msg_payload_dict["data"]["end_time"]
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                begin_time = int(time.mktime(time.strptime(start_time, '%Y-%m-%d')))
                end_time_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))
                allure.attach("Expect begin time stamp:", str(begin_time))
                allure.attach("Actual begin time stamp:", str(begin_time_payload))
                allure.attach("Expect end time stamp:", str(end_time_stamp))
                allure.attach("Actual end time stamp:", str(end_time_payload))
                allure.attach("Expect verify condition type:", str(1))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert begin_time_payload == str(begin_time)
                assert end_time_payload == str(end_time_stamp)
                assert verify_condition_type_payload == str(1)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_begin_time_and_end_time_1 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为2时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-009")
    def test_003009_get_payload_begin_time_and_end_time_2(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_2 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the begin time and end time in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                begin_time_payload = msg_payload_dict["data"]["begin_time"]
                end_time_payload = msg_payload_dict["data"]["end_time"]
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                # begin_time = int(time.mktime(time.strptime(start_time, '%Y-%m-%d')))
                # allure.attach("Expect begin time stamp:", str(begin_time))
                allure.attach("Actual begin time stamp:", str(begin_time_payload))
                allure.attach("Expect end time stamp:", str(9999999999))
                allure.attach("Actual end time stamp:", str(end_time_payload))
                allure.attach("Expect verify condition type:", str(2))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                # assert begin_time_payload == str(begin_time)
                assert end_time_payload == str(9999999999)
                assert verify_condition_type_payload == str(2)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_begin_time_and_end_time_2 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为3时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-010")
    def test_003010_get_payload_begin_time_and_end_time_3(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_3 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the begin time and end time in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                begin_time_payload = msg_payload_dict["data"]["begin_time"]
                end_time_payload = msg_payload_dict["data"]["end_time"]
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                begin_time = int(time.mktime(time.strptime(start_time, '%Y-%m-%d')))
                end_time_stamp = int(time.mktime(time.strptime(end_time, '%Y-%m-%d')))
                allure.attach("Expect begin time stamp:", str(begin_time))
                allure.attach("Actual begin time stamp:", str(begin_time_payload))
                allure.attach("Expect end time stamp:", str(end_time_stamp))
                allure.attach("Actual end time stamp:", str(end_time_payload))
                allure.attach("Expect verify condition type:", str(1))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert end_time_payload == str(end_time_stamp)
                assert verify_condition_type_payload == str(3)
                assert begin_time_payload == str(begin_time)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_begin_time_and_end_time_3 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的in_count")
    @allure.testcase("FT-HTJK-003-011")
    def test_003011_get_payload_in_count(self):
        self.logger.info("....test_get_payload_in_count ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the in_count in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                in_count_payload = msg_payload_dict["data"]["in_count"]
                with allure.step("get in_count in db"):
                    table = 'bus_sku'
                    condition = ("sku_id", sku_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    in_count = select_result[0][16]
                allure.attach("Expect in count:", str(in_count))
                allure.attach("Actual in count:", str(in_count_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                assert in_count_payload == str(in_count)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_in_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为1时,服务单下发payload的in_count为0")
    @allure.testcase("FT-HTJK-003-012")
    def test_003012_get_payload_in_count_1(self):
        self.logger.info("....test_get_payload_in_count_1 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the in_count in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                in_count_payload = msg_payload_dict["data"]["in_count"]
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                with allure.step("get in_count in db"):
                    table = 'bus_sku'
                    condition = ("sku_id", sku_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    in_count = select_result[0][16]
                allure.attach("Expect in count:", str(in_count))
                allure.attach("Actual in count:", str(in_count_payload))
                allure.attach("Expect verify condition type:", str(1))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == str(in_count)
                assert verify_condition_type_payload == str(1)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_in_count_1 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为2时,服务单下发payload的in_count大于0")
    @allure.testcase("FT-HTJK-003-013")
    def test_003013_get_payload_in_count_2(self):
        self.logger.info("....test_get_payload_in_count_2 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the in_count in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                in_count_payload = int(msg_payload_dict["data"]["in_count"])
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                with allure.step("get in_count in db"):
                    table = 'bus_sku'
                    condition = ("sku_id", sku_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    in_count = select_result[0][16]
                allure.attach("Expect in count:", str(in_count))
                allure.attach("Actual in count:", str(in_count_payload))
                allure.attach("Expect verify condition type:", str(2))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == in_count
                assert in_count_payload > 0
                assert verify_condition_type_payload == str(2)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_in_count_2 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为3时,服务单下发payload的in_count大于0")
    @allure.testcase("FT-HTJK-003-014")
    def test_003014_get_payload_in_count_3(self):
        self.logger.info("....test_get_payload_in_count_2 ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the in_count in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                in_count_payload = int(msg_payload_dict["data"]["in_count"])
                verify_condition_type_payload = msg_payload_dict["data"]["verify_condition_type"]
                with allure.step("get in_count in db"):
                    table = 'bus_sku'
                    condition = ("sku_id", sku_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    in_count = select_result[0][16]
                allure.attach("Expect in count:", str(in_count))
                allure.attach("Actual in count:", str(in_count_payload))
                allure.attach("Expect verify condition type:", str(3))
                allure.attach("Actual verify condition type:", str(verify_condition_type_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == in_count
                assert in_count_payload > 0
                assert verify_condition_type_payload == str(3)
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_in_count_3 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的extra")
    @allure.testcase("FT-HTJK-003-015")
    def test_003015_get_payload_extra(self):
        self.logger.info("....test_get_payload_extra ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep5:assert the extra in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                extra_payload = msg_payload_dict["data"]["extra"]
                allure.attach("Expect len of extra:", "more than 0")
                allure.attach("Actual extra:", str(extra_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual extra:{0}".format(extra_payload))
                assert len(extra_payload) > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_extra ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的timestamp")
    @allure.testcase("FT-HTJK-003-016")
    def test_003016_get_payload_timestamp(self):
        self.logger.info("....test_get_payload_timestamp ....")
        topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:get sku id"):
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                table = 'bus_sku'
                condition = ("name", sku_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]
            with allure.step("teststep3:issued the service order"):
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(self.httpclient2, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                now = datetime.datetime.now()
                start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                r_applyresult1 = h5_shopping_apply_result(self.httpclient2, self.provider_id, self.spu_id, sku_id,
                                                          [self.features_id], start_time, end_time, self.logger)
                allure.attach("apply result", str(r_applyresult1))
                self.logger.info("apply result: " + str(r_applyresult1))
                assert r_applyresult1
            with allure.step("teststep4:get service order id"):
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
            with allure.step("teststep3:assert the timestamp in payload"):
                d_start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    d_end_time = datetime.datetime.now()
                    during = (d_end_time - d_start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                timestamp_payload = int(msg_payload_dict["timestamp"])
                table_name = "bus_service_order"
                condition = ("service_order_id", self.service_order_id)
                timestamp = self.mysql.execute_select_condition(table_name, condition)[0][19]
                allure.attach("Expect timestamp:", str(timestamp))
                allure.attach("Actual timestamp:", str(timestamp_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert timestamp_payload <= timestamp + 5
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info("....End test_get_payload_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_IOT_ServiceOrder_Push.py'])
    pytest.main(['-s', 'test_IOT_ServiceOrder_Push.py::TestServiceOrderPush::test_003001_get_payload_action_id'])
