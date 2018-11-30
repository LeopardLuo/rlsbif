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


@allure.feature("IOT-时间同步响应")
class TestTimeSynchronizationResponse(object):

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
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        self.logger.info("Add some datas to database.")
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("时间同步响应，下发payload的action_id")
    @allure.testcase("FT-HTJK-003-52")
    def test_003052_get_payload_action_id_time_synchronization_response(self):
        self.logger.info(".... test_003052_get_payload_action_id_time_synchronization_response ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                stamp = get_timestamp()
                send_payload = '{"action_id":"104","data":null, "timestamp:"' + str(stamp) + '}'
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, send_payload, 1)
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
                allure.attach("Expect action id:", "204")
                allure.attach("Actual action id:", str(action_id))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                assert action_id == "204"

        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003052_get_payload_action_id_time_synchronization_response ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("时间同步响应，下发payload的timestamp")
    @allure.testcase("FT-HTJK-003-53")
    def test_003053_get_payload_timestamp_time_synchronization_response(self):
        self.logger.info(".... test_003053_get_payload_timestamp_time_synchronization_response ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                stamp = get_timestamp()
                send_payload = '{"action_id":"104","data":null, "timestamp:"' + str(stamp) + '}'
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, send_payload, 1)
                self.logger.info("publish the request ")
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
                self.logger.info("Actual action id:{0}".format(timestamp_payload))
                assert int(timestamp_payload) == local_timestamp
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003053_get_payload_timestamp_time_synchronization_response ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_IOT_Time_Synchronization_Response.py'])
