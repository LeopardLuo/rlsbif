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


@allure.feature("服务单下发")
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
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        with allure.step("delete service order"):
            table = 'bus_service_order'
            condition = ("member_id", "23834536681144320")
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
    @allure.story("服务单下发payload的action_id")
    @allure.testcase("FT-HTJK-003-001")
    def test_003001_get_payload_action_id(self):
        self.logger.info(".... test_003001_get_payload_action_id ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通AI产品部4"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the action_id in payload"):
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
                allure.attach("Actual action id:", action_id)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "201"
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_003001_get_payload_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的服务单流水号")
    @allure.testcase("FT-HTJK-003-002")
    def test_003002_get_payload_service_order_id(self):
        self.logger.info(".... test_003002_get_payload_service_order_id ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通AI产品部4"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the service order id in payload"):
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
                allure.attach("Expect service order id:", service_order_id)
                allure.attach("Actual service order id:", service_order_id_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual service order id:{0}".format(service_order_id_payload))
                assert service_order_id_payload == str(service_order_id)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_003002_get_payload_service_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的特征串")
    @allure.testcase("FT-HTJK-003-003")
    def test_003003_get_payload_feature(self):
        self.logger.info(".... test_003003_get_payload_feature ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通AI产品部4"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the feature in payload"):
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
                condition = ("features_id", "23854189239205888")
                feature = self.mysql.execute_select_condition(table_name, condition)[0][6]
                allure.attach("Expect feature:", feature)
                allure.attach("Actual feature:", feature_in_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual feature:{0}".format(feature_in_payload))
                assert feature_in_payload == feature
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_003003_get_payload_feature ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的特征类型")
    @allure.testcase("FT-HTJK-003-004")
    def test_003004_get_payload_feature_type(self):
        self.logger.info(".... test_003004_get_payload_feature_type ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通AI产品部4"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the feature type in payload"):
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
                condition = ("features_id", "23854189239205888")
                feature_type = self.mysql.execute_select_condition(table_name, condition)[0][4]
                allure.attach("Expect feature type:", feature_type)
                allure.attach("Actual feature type:", feature_type_payload_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual feature type:{0}".format(feature_type_payload_payload))
                assert feature_type_payload_payload == str(feature_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_003004_get_payload_feature_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的verify_condition_type")
    @allure.testcase("FT-HTJK-003-005")
    def test_003005_get_payload_verify_condition_type(self):
        self.logger.info(".... test_003005_get_payload_verify_condition_type ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通AI产品部4"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the verify condition type in payload"):
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
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_003005_get_payload_verify_condition_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的begin_time")
    @allure.testcase("FT-HTJK-003-006")
    def test_003006_get_payload_begin_time(self):
        self.logger.info(".... test_003006_get_payload_begin_time ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the begin time in payload"):
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
                allure.attach("Expect begin time:", begin_time)
                allure.attach("Actual begin time:", begin_time_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time:{0}".format(begin_time_payload))
                assert begin_time_payload == str(begin_time)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_003006_get_payload_begin_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的end_time")
    @allure.testcase("FT-HTJK-003-007")
    def test_003007_get_payload_end_time(self):
        self.logger.info(".... test_003007_get_payload_end_time ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = 1539843055
                end_time = 9999999999
                in_count = 4
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the end time in payload"):
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
                allure.attach("Expect end time:", end_time)
                allure.attach("Actual end time:", end_time_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual end time:{0}".format(end_time_payload))
                assert end_time_payload == str(end_time)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_003007_get_payload_end_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为1时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-008")
    def test_003008_get_payload_begin_time_and_end_time_1(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_1 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 0
                verify_condition_type = 1
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the begin time and end time in payload"):
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
                allure.attach("Expect begin time stamp:", begin_time)
                allure.attach("Actual begin time stamp:", begin_time_payload)
                allure.attach("Expect end time stamp:", end_time)
                allure.attach("Actual end time stamp:", end_time_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert begin_time_payload == str(begin_time)
                assert end_time_payload == str(end_time)
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_begin_time_and_end_time_1 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为2时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-009")
    def test_003009_get_payload_begin_time_and_end_time_2(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_2 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = 9999999999
                in_count = 2
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the begin time and end time in payload"):
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
                allure.attach("Expect begin time stamp:", begin_time)
                allure.attach("Actual begin time stamp:", begin_time_payload)
                allure.attach("Expect end time stamp:", end_time)
                allure.attach("Actual end time stamp:", end_time_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert begin_time_payload == str(begin_time)
                assert end_time_payload == str(end_time)
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_begin_time_and_end_time_2 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为3时,服务单下发payload的begin_time与end_time")
    @allure.testcase("FT-HTJK-003-010")
    def test_003010_get_payload_begin_time_and_end_time_3(self):
        self.logger.info("....test_get_payload_begin_time_and_end_time_3 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 2
                verify_condition_type = 3
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the begin time and end time in payload"):
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
                allure.attach("Expect begin time stamp:", begin_time)
                allure.attach("Actual begin time stamp:", begin_time_payload)
                allure.attach("Expect end time stamp:", end_time)
                allure.attach("Actual end time stamp:", end_time_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual begin time stamp:{0}".format(begin_time_payload))
                self.logger.info("Actual end time stamp:{0}".format(end_time_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert begin_time_payload == str(begin_time)
                assert end_time_payload == str(end_time)
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_begin_time_and_end_time_3 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的in_count")
    @allure.testcase("FT-HTJK-003-011")
    def test_003011_get_payload_in_count(self):
        self.logger.info("....test_get_payload_in_count ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 5
                verify_condition_type = 3
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the in_count in payload"):
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
                allure.attach("Expect in count:", in_count)
                allure.attach("Actual in count:", in_count_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                assert in_count_payload == str(in_count)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_in_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为1时,服务单下发payload的in_count为0")
    @allure.testcase("FT-HTJK-003-012")
    def test_003012_get_payload_in_count_1(self):
        self.logger.info("....test_get_payload_in_count_1 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 0
                verify_condition_type = 1
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the in_count in payload"):
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
                allure.attach("Expect in count:", in_count)
                allure.attach("Actual in count:", in_count_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == str(0)
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_in_count_1 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为2时,服务单下发payload的in_count大于0")
    @allure.testcase("FT-HTJK-003-013")
    def test_003013_get_payload_in_count_2(self):
        self.logger.info("....test_get_payload_in_count_2 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = 9999999999
                in_count = 2
                verify_condition_type = 2
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the in_count in payload"):
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
                allure.attach("Expect in count:", in_count)
                allure.attach("Actual in count:", in_count_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == in_count
                assert in_count > 0
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_in_count_2 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("verify_condition_type为3时,服务单下发payload的in_count大于0")
    @allure.testcase("FT-HTJK-003-014")
    def test_003013_get_payload_in_count_3(self):
        self.logger.info("....test_get_payload_in_count_2 ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 2
                verify_condition_type = 3
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the in_count in payload"):
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
                allure.attach("Expect in count:", in_count)
                allure.attach("Actual in count:", in_count_payload)
                allure.attach("Expect verify condition type:", verify_condition_type)
                allure.attach("Actual verify condition type:", verify_condition_type_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual in count:{0}".format(in_count_payload))
                self.logger.info("Actual verify condition type:{0}".format(verify_condition_type_payload))
                assert in_count_payload == in_count
                assert in_count > 0
                assert verify_condition_type_payload == str(verify_condition_type)
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_in_count_3 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的exrea")
    @allure.testcase("FT-HTJK-003-015")
    def test_003015_get_payload_exrea(self):
        self.logger.info("....test_get_payload_exrea ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 0
                verify_condition_type = 1
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
            with allure.step("teststep3:assert the exrea in payload"):
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
                exrea_payload = msg_payload_dict["data"]["exrea"]
                allure.attach("Expect exrea:", "")
                allure.attach("Actual exrea:", exrea_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual exrea:{0}".format(exrea_payload))
                assert exrea_payload is not None
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_exrea ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单下发payload的timestamp")
    @allure.testcase("FT-HTJK-003-016")
    def test_003016_get_payload_timestamp(self):
        self.logger.info("....test_get_payload_timestamp ....")
        try:
            with allure.step("teststep1: subscribe the topic."):
                topic = "/{0}/{1}/ServiceOrderPush".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:issued the service order"):
                self.logger.info("strat to create service order.")
                system_id = "15596785737138176"
                random_num = ""
                # 生成随机4位数
                for i in range(4):
                    ch = chr(random.randrange(ord('0'), ord('9') + 1))
                    random_num += ch
                business_order_id = str(get_timestamp()) + random_num
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                member_id = 23834536681144320
                features_id = 23854189239205888
                service_unit = "慧睿思通公共技术平台部"
                service_address = "广州番禺区北大街"
                begin_time = get_timestamp() + 300
                end_time = get_timestamp() + 3000
                in_count = 0
                verify_condition_type = 1
                device_ids = ["23912662580592640"]
                create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                      member_id, system_code, features_id, device_ids,
                                                                      verify_condition_type, begin_time, end_time,
                                                                      in_count, service_unit, service_address,
                                                                      logger=self.logger)
                service_order_id = 0
                if create_service_order_result:
                    service_order_id = create_service_order_result["service_order_id"]
                    self.logger.info("service order id:" + str(service_order_id))
                else:
                    self.logger.info("create service order failed.")
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
                condition = ("service_order_id", service_order_id)
                timestamp = self.mysql.execute_select_condition(table_name, condition)[0][16]
                allure.attach("Expect timestamp:", timestamp)
                allure.attach("Actual timestamp:", timestamp_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert timestamp_payload <= timestamp + 5
                self.mqtt_client.unsubscribe(topic)
                self.mqtt_client.loopstop()
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info("....End test_get_payload_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_ServiceOrder_Push.py'])
    # system_id = "15596785737138176"
    # random_num = ""
    # # 生成随机4位数
    # for i in range(4):
    #     ch = chr(random.randrange(ord('0'), ord('9') + 1))
    #     random_num += ch
    # business_order_id = str(get_timestamp()) + random_num
    # system_code = "ba80b269044e7501d1b4e7890d319ff5"
    # member_id = 23834536681144320
    # features_id = 23854189239205888
    # service_unit = "慧睿思通AI产品部4"
    # service_address = "广州番禺区北大街"
    # begin_time = 1539843055
    # end_time = get_timestamp()+ 3000
    # in_count = 0
    # verify_condition_type = 1
    # device_ids = ["23912662580592640"]
    # test_http_client = HTTPClient("http://192.168.3.46:80")
    # test_logger = Logger()
    # create_service_order_result = h5_create_service_order(test_http_client, system_id, business_order_id, member_id,
    #                                                       system_code, features_id, device_ids, verify_condition_type,
    #                                                       begin_time, end_time, in_count, service_unit, service_address,
    #                                                       logger=test_logger)
    # print(create_service_order_result)
    # service_order = create_service_order_result["service_order_id"]
    # test_mysql = MysqlClient("root","hrst123","192.168.3.46","zngz")
    # table_name = "bus_service_order"
    # condition = ("service_order_id", service_order)
    # time.sleep(5)
    # table_name2 = "mem_features"
    # condition2 = ("features_id", "23854189239205888")
    # mysql_result2 = test_mysql.execute_select_condition(table_name2, condition2)
    # feature_type = mysql_result2[0][4]
    # test_logger.info("sql result2:{0}".format(mysql_result2))
    # test_logger.info("feature_type result:{0}".format(feature_type))
    # mysql_result = test_mysql.execute_select_condition(table_name, condition)
    # t_stamp = mysql_result[0][16]
    # test_logger.info("sql result:{0}".format(mysql_result))
    # test_logger.info("t_stamp result:{0}".format(t_stamp))
    # test_mysql.close()
    # test_http_client.close()
