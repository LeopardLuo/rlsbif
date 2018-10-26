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


@allure.feature("服务单关闭")
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
                cls.params = AliParam(ProductKey=cls.ProductKey, DeviceName=cls.DeviceName,
                                      DeviceSecret=cls.DeviceSecret)
                cls.clientid, cls.username, cls.password, cls.hostname = cls.params.get_param()
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
            with allure.step("注册用户，生成member_id"):
                code_type = 2
                client_type = 2
                client_version = "v1"
                device_token = "138001380001234"
                imei = "138001380001234"
                phone = "13800138000"
                sms_code = "123456"
                login_result = make_login(cls.httpclient, code_type, client_type, client_version, device_token, imei,
                                          phone, sms_code,logger=cls.logger)
                if login_result == {}:
                    cls.logger.error("user login failed!")
                    assert False
                cls.member_id = login_result["user_info"]["member_id"]
                cls.token = login_result['token']
            with allure.step("进行身份认证，获取feature_id"):
                headers = {"authorization": cls.token}
                identity_card_face = "D:\\test_photo\\fore2.jpg"
                identity_card_emblem = "D:\\test_photo\\back2.jpg"
                face_picture = "D:\\test_photo\\face2.jpg"
                cls.httpclient.update_header(headers)
                user_identity_result = user_identity(cls.httpclient, cls.member_id, identity_card_face, identity_card_emblem,
                                                     face_picture, logger=cls.logger)
                if not user_identity_result:
                    cls.logger.error("user identity failed!")
                    assert False
                table_name = "mem_features"
                condition = ("member_id",cls.member_id)
                cls.features_id = cls.mysql.execute_select_condition(table_name,condition)[0][0]
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
        with allure.step("delete member"):
            member_table = "mem_member"
            mem_condition = ("member_id",cls.member_id)
            allure.attach("table name", str(member_table))
            cls.logger.info("table: {0}".format(member_table))
            mem_delete_result = cls.mysql.execute_delete_condition(member_table, mem_condition)
            allure.attach("delete result", str(mem_delete_result))
            cls.logger.info("delete result: {0}".format(mem_delete_result))
        with allure.step("delete feature"):
            features_table = "mem_features"
            features_condition = ("features_id",cls.features_id)
            allure.attach("table name", str(features_table))
            cls.logger.info("table: {0}".format(features_table))
            features_delete_result = cls.mysql.execute_delete_condition(features_table, features_condition)
            allure.attach("delete result", str(features_delete_result))
            cls.logger.info("delete result: {0}".format(features_delete_result))
        if hasattr(cls, 'mqtt_client'):
            cls.mqtt_client.close()
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, "mysql"):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        with allure.step("创建服务单"):
            self.logger.info("strat to create service order.")
            system_id = "15596785737138176"
            random_num = ""
            # 生成随机4位数
            for i in range(4):
                ch = chr(random.randrange(ord('0'), ord('9') + 1))
                random_num += ch
            business_order_id = str(get_timestamp()) + random_num
            system_code = "ba80b269044e7501d1b4e7890d319ff5"
            member_id = self.member_id
            features_id = self.features_id
            service_unit = "慧睿思通AI产品部4"
            service_address = "广州番禺区北大街"
            begin_time = get_timestamp() + 300
            end_time = 9999999999
            in_count = 4
            verify_condition_type = 2
            device_ids = ["23912662580592640"]
            create_service_order_result = h5_create_service_order(self.httpclient, system_id, business_order_id,
                                                                  member_id, system_code, features_id, device_ids,
                                                                  verify_condition_type, begin_time, end_time,
                                                                  in_count, service_unit, service_address,
                                                                  logger=self.logger)
            if create_service_order_result:
                self.service_order_id = create_service_order_result["service_order_id"]
                self.logger.info("service order id:" + str(self.service_order_id))
            else:
                self.logger.info("create service order failed.")
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        with allure.step("delete bus service order status"):
            table = 'bus_service_order_status'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete service order"):
            table = 'bus_service_order'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("服务单关闭，下发payload的action_id")
    @allure.testcase("FT-HTJK-003-033")
    @pytest.mark.parametrize("close_code,result",
                             [(0, '203'), (1, '203')],
                             ids=["close_code为0(正常关闭服务单)", "close_code为1(撤销服务单)"])
    def test_003033_get_payload_action_id_after_closed(self,close_code,result):
        self.logger.info(".... test_003033_get_payload_action_id_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                system_id = "15596785737138176"
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                # close_code1 = 0
                close_service_order_result = bs_close_service_order(self.httpclient, system_id, self.service_order_id,
                                                                      system_code, close_code,
                                                                      logger=self.logger)
                if close_service_order_result:
                    self.logger.info("close service order success." )
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
                allure.attach("Expect action id:", result)
                allure.attach("Actual action id:", action_id)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == result
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
    @pytest.mark.parametrize("close_code",
                             [(0), (1)],
                             ids=["close_code为0(正常关闭服务单)", "close_code为1(撤销服务单)"])
    def test_003034_get_payload_service_order_id_after_closed(self,close_code):
        self.logger.info(".... test_003034_get_payload_service_order_id_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                system_id = "15596785737138176"
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                # close_code = 0
                close_service_order_result = bs_close_service_order(self.httpclient, system_id, self.service_order_id,
                                                                     system_code, close_code,
                                                                     logger=self.logger)
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
                allure.attach("Expect service_order_id:", self.service_order_id)
                allure.attach("Actual service_order_id:", service_order_id_payload)
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
    @pytest.mark.parametrize("close_code",
                             [(0), (1)],
                             ids=["close_code为0(正常关闭服务单)", "close_code为1(撤销服务单)"])
    def test_003035_get_payload_timestamp_after_closed(self,close_code):
        self.logger.info(".... test_003035_get_payload_timestamp_after_closed ....")
        topic = "/{0}/{1}/ServiceOrderClose".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:close the service order"):
                self.logger.info("strat to close service order.")
                system_id = "15596785737138176"
                system_code = "ba80b269044e7501d1b4e7890d319ff5"
                # close_code = 0
                timestamp = get_timestamp()
                close_service_order_result = bs_close_service_order(self.httpclient, system_id, self.service_order_id,
                                                                     system_code, close_code, timestamp,
                                                                     logger=self.logger)
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
                allure.attach("Expect timestamp:", timestamp)
                allure.attach("Actual timestamp:", timestamp_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert int(timestamp_payload) <= timestamp+5
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
    pytest.main(['-s', 'test_ServiceOrder_Close.py'])
