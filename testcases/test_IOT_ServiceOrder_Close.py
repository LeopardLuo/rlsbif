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


@allure.feature("IoT-服务单关闭")
class TestServiceOrderClose(object):

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
            device_token = "1"*44
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
            now = datetime.datetime.now()
            start_time = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            end_time = (now + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
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
    @allure.story("服务单关闭，下发payload的action_id")
    @allure.testcase("FT-HTJK-003-033")
    def test_003033_get_payload_action_id_after_closed(self):
        self.logger.info(".... test_003033_get_payload_action_id_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                close_service_order_result = h5_order_delete(self.httpclient2, self.provider_id, self.spu_id,
                                                             self.sku_id, self.bus_order_id, logger=None)
                if close_service_order_result:
                    self.logger.info("close service order success.")
                else:
                    self.logger.info("close service order failed.")
            with allure.step("teststep3:assert the action_id in payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                # time.sleep(5)
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                allure.attach("Expect action id:", str(203))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "203"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003033_get_payload_action_id_after_closed ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单关闭，下发payload的service_order_id")
    @allure.testcase("FT-HTJK-003-034")
    def test_003034_get_payload_service_order_id_after_closed(self):
        self.logger.info(".... test_003034_get_payload_service_order_id_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                close_service_order_result = h5_order_delete(self.httpclient2, self.provider_id, self.spu_id,
                                                             self.sku_id, self.bus_order_id, logger=None)
                if close_service_order_result:
                    self.logger.info("close service order success.")
                else:
                    self.logger.info("close service order failed.")
            with allure.step("teststep3:assert the service_order_id in payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                # time.sleep(5)
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                service_order_id_payload = msg_payload_dict["data"]["service_order_id"]
                allure.attach("Expect service_order_id:", str(self.service_order_id))
                allure.attach("Actual service_order_id:", str(service_order_id_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual service_order_id:{0}".format(service_order_id_payload))
                assert int(service_order_id_payload) == self.service_order_id
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003034_get_payload_service_order_id_after_closed ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单关闭，下发payload的timestamp")
    @allure.testcase("FT-HTJK-003-035")
    def test_003035_get_payload_timestamp_after_closed(self):
        self.logger.info(".... test_003035_get_payload_timestamp_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                close_service_order_result = h5_order_delete(self.httpclient2, self.provider_id, self.spu_id,
                                                             self.sku_id, self.bus_order_id, logger=None)
                if close_service_order_result:
                    self.logger.info("close service order success.")
                else:
                    self.logger.info("close service order failed.")
            with allure.step("teststep3:assert the timestamp in payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                # time.sleep(5)
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                timestamp_payload = msg_payload_dict["timestamp"]
                local_timestamp = get_timestamp()
                allure.attach("Expect timestamp:", str(local_timestamp))
                allure.attach("Actual timestamp:", str(timestamp_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert local_timestamp-10 <=int(timestamp_payload) <= local_timestamp
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003035_get_payload_timestamp_after_closed ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_IOT_ServiceOrder_Close.py'])
    pytest.main(
        ['-s', 'test_IOT_ServiceOrder_Close.py::TestServiceOrderClose::test_003033_get_payload_action_id_after_closed'])
