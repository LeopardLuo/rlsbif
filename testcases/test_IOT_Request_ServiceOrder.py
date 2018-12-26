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

@pytest.mark.skip(reason="设备向平台请求指定时间的服务单未开发完成")
@pytest.mark.IOT
@allure.feature("IOT-设备向平台请求指定时间的服务单")
class TestRequestServiceOrder(object):

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
            with allure.step("初始化HTTP客户端2。"):
                h5_port = cls.config.getItem('h5', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, h5_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient2 = HTTPClient(baseurl)
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
            device_token = "1234" * 11
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
    @allure.story("设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-001")
    def test_310001_request_service_order_normal(self):
        self.logger.info(".... test_310001_request_service_order_normal ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310001_request_service_order_normal ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误action_id，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-002")
    @pytest.mark.parametrize("action_id, result",
                             [('109', []), ('106' * 10, []), ('1.0', []), ('中', []), ('a', []), ('*', []), ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["action_id(非106)", "action_id(超长值)", "action_id(小数)", "action_id(中文)",
                                  "action_id(字母)", "action_id(特殊字符)", "action_id(数字字母)", "action_id(数字中文)",
                                  "action_id(数字特殊字符)", "action_id(空格)", "action_id(空)"])
    def test_310002_request_service_order_incorrect_action_id(self, action_id, result):
        self.logger.info(".... test_310002_request_service_order_incorrect_action_id ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": action_id,
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310002_request_service_order_incorrect_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误device_id，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-002")
    @pytest.mark.parametrize("device_id, result",
                             [('33912662580592640', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []),
                              ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["device_id(非增加设备id值)", "device_id(超长值)", "device_id(小数)", "device_id(中文)",
                                  "device_id(字母)", "device_id(特殊字符)", "device_id(数字字母)", "device_id(数字中文)",
                                  "device_id(数字特殊字符)", "device_id(空格)", "device_id(空)"])
    def test_310003_request_service_order_incorrect_device_id(self, device_id, result):
        self.logger.info(".... test_310002_request_service_order_incorrect_action_id ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310003_request_service_order_incorrect_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正确的begin_time,设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-004")
    @pytest.mark.parametrize("begin_time",
                             [(1), (get_timestamp())],
                             ids=["begin_time(支持最早的日期时间)", "begin_time(当前时间戳)"])
    def test_310004_request_service_order_correct_begin_time(self, begin_time):
        self.logger.info(".... test_310004_request_service_order_correct_begin_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                # begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310004_request_service_order_correct_begin_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误begin_time，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-005")
    @pytest.mark.parametrize("begin_time, result",
                             [(9223372036854775807, []), (-9223372036854775809, []),
                              (9223372036854775808, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["begin_time(最大值)",
                                  "begin_time(超小值)", "begin_time(超大值)",
                                  "begin_time(字母)", "begin_time(中文)", "begin_time(特殊字符)", "begin_time(数字字母)",
                                  "begin_time(数字中文)",
                                  "begin_time(数字特殊字符)", "begin_time(空格)", "begin_time(空)"])
    def test_310005_request_service_order_incorrect_begin_time(self, begin_time, result):
        self.logger.info(".... test_310005_request_service_order_incorrect_begin_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                # begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310005_request_service_order_incorrect_begin_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正确的end_time,设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-006")
    @pytest.mark.parametrize("end_time",
                             [(get_timestamp()), (get_timestamp() + 20)],
                             ids=["end_time(支持最早的日期时间)", "end_time(当前时间戳)"])
    def test_310006_request_service_order_correct_end_time(self, end_time):
        self.logger.info(".... test_310006_request_service_order_correct_end_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                # end_time = end_time
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310006_request_service_order_correct_end_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误end_time，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-007")
    @pytest.mark.parametrize("end_time, result",
                             [((get_timestamp() - 60), []), (9223372036854775807, []), (-9223372036854775809, []),
                              (9223372036854775808, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["end_time(end_time小于begin_time)", "end_time(最大值)",
                                  "end_time(超小值)", "end_time(超大值)",
                                  "end_time(字母)", "end_time(中文)", "end_time(特殊字符)", "end_time(数字字母)",
                                  "end_time(数字中文)",
                                  "end_time(数字特殊字符)", "end_time(空格)", "end_time(空)"])
    def test_310007_request_service_order_incorrect_end_time(self, end_time, result):
        self.logger.info(".... test_310007_request_service_order_incorrect_end_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 50
                # end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310007_request_service_order_incorrect_end_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置data_type值为0,设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-008")
    def test_310008_request_service_order_correct_data_type_0(self):
        self.logger.info(".... test_310008_request_service_order_correct_data_type_0 ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep4:get the service order of device from db"):
                table = "bus_service_order_status"
                sub_select1 = "SELECT service_order_id FROM bus_service_order WHERE created_time BETWEEN {0} AND {1}".format(
                    begin_time, end_time)
                sub_select2 = "SELECT service_order_id FROM bus_service_order_device_list WHERE device_id={0} and service_order_id in ({1})".format(
                    self.device_id, sub_select1)
                condition = "service_order_id in ({0})".format(sub_select2)
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310008_request_service_order_correct_data_type_0 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置data_type值为1,设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-009")
    def test_310009_request_service_order_correct_data_type_1(self):
        self.logger.info(".... test_310009_request_service_order_correct_data_type_1 ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 1}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep4:get the service order of device from db"):
                table = "bus_service_order_status"
                sub_select1 = "SELECT service_order_id FROM bus_service_order WHERE created_time BETWEEN {0} AND {1}".format(
                    begin_time, end_time)
                sub_select2 = "SELECT service_order_id FROM bus_service_order_device_list WHERE device_id={0} and service_order_id in ({1})".format(
                    self.device_id, sub_select1)
                condition = "service_order_id in ({0}) and state <3".format(sub_select2)
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310009_request_service_order_correct_data_type_1 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置data_type值为2,设备正常向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-010")
    def test_310010_request_service_order_correct_data_type_2(self):
        self.logger.info(".... test_310010_request_service_order_correct_data_type_2 ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 2}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep4:get the service order of device from db"):
                table = "bus_service_order_status"
                sub_select1 = "SELECT service_order_id FROM bus_service_order WHERE created_time BETWEEN {0} AND {1}".format(
                    begin_time, end_time)
                sub_select2 = "SELECT service_order_id FROM bus_service_order_device_list WHERE device_id={0} and service_order_id in ({1})".format(
                    self.device_id, sub_select1)
                condition = "service_order_id in ({0}) and state >= 3".format(sub_select2)
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310010_request_service_order_correct_data_type_2 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误data_type，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-011")
    @pytest.mark.parametrize("data_type, result",
                             [(3, []), (9223372036854775807, []), (1.5, []),
                              ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["data_type(非'0,1,2')", "data_type(超长值)",
                                  "data_type(小数)", "data_type(字母)", "data_type(中文)",
                                  "data_type(特殊字符)", "data_type(数字字母)", "data_type(数字中文)",
                                  "data_type(数字特殊字符)", "data_type(空格)", "data_type(空)"])
    def test_310011_request_service_order_incorrect_data_type(self, data_type, result):
        self.logger.info(".... test_310011_request_service_order_incorrect_data_type ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": data_type}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310011_request_service_order_incorrect_data_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正确timestamp,设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-012")
    @pytest.mark.parametrize("timestamp",
                             [(1), (9999999999)],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_310012_request_service_order_correct_timestamp(self, timestamp):
        self.logger.info(".... test_310012_request_service_order_correct_timestamp ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
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
                allure.attach("Expect action id:", str(206))
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "206"
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310012_request_service_order_correct_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误timestamp，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-013")
    @pytest.mark.parametrize("timestamp, result",
                             [(9223372036854775807, []), (0, []), (-1, []), (-9223372036854775809, []),
                              (9223372036854775808, []), (1.5, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_310013_request_service_order_incorrect_timestamp(self, timestamp, result):
        self.logger.info(".... test_310013_request_service_order_incorrect_timestamp ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str(result))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310013_request_service_order_incorrect_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少action_id，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-014")
    def test_310014_request_service_order_no_action_id(self):
        self.logger.info(".... test_310014_request_service_order_no_action_id ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310014_request_service_order_no_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_id，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-015")
    def test_310015_request_service_order_no_device_id(self):
        self.logger.info(".... test_310015_request_service_order_no_device_id ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310015_request_service_order_no_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少begin_time，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-016")
    def test_310016_request_service_order_no_begin_time(self):
        self.logger.info(".... test_310016_request_service_order_no_begin_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                # begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id":self.device_id, "end_time": end_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310016_request_service_order_no_begin_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少end_time，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-017")
    def test_310017_request_service_order_no_end_time(self):
        self.logger.info(".... test_310017_request_service_order_no_end_time ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                # end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time,
                                         "data_type": 0}, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310017_request_service_order_no_end_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少data_type，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-018")
    def test_310018_request_service_order_no_data_type(self):
        self.logger.info(".... test_310018_request_service_order_no_data_type ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time,"end_time":end_time},
                                "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310018_request_service_order_no_data_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp，设备向平台请求指定时间的服务单")
    @allure.testcase("FT-HTJK-310-019")
    def test_310019_request_service_order_no_timestamp(self):
        self.logger.info(".... test_310019_request_service_order_no_timestamp ....")
        topic = "/{0}/{1}/Common/Down".format(self.ProductKey, self.DeviceName)
        send_topic = "/{0}/{1}/Common/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request service orders"):
                self.logger.info("request service orders.")
                stamp = get_timestamp()
                begin_time = stamp - 3600
                end_time = stamp + 3600
                send_payload = {"action_id": "106",
                                "data": {"device_id": self.device_id, "begin_time": begin_time, "end_time": end_time,
                                         "data_type": 0}}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                time.sleep(15)
                mqtt_msg = self.mqtt_client.rcv_msg
                allure.attach("Expect payload:", str([]))
                allure.attach("Actual payload:", str(mqtt_msg))
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            while self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_310019_request_service_order_no_timestamp ....")
            self.logger.info("")
