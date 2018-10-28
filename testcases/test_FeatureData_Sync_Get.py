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


@allure.feature("特征同步上报")
class TestFeatureDataSyncReport(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()
        cls.device_id = "23912662580592640"
        cls.logger.info("")
        cls.logger.info("*** The setup class method.")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("初始化MQTT客户端1"):
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
            with allure.step("初始化MQTT客户端2"):
                # 读取配置文件，获取IOT服务端所需参数
                cls.ProductKey2 = cls.config.getItem("device", "d2_productkey")
                cls.DeviceName2 = cls.config.getItem("device", "d2_devicename")
                cls.DeviceSecret2 = cls.config.getItem("device", "d2_secret")
                cls.params2 = AliParam(ProductKey=cls.ProductKey2, DeviceName=cls.DeviceName2,
                                      DeviceSecret=cls.DeviceSecret2)
                cls.clientid2, cls.username2, cls.password2, cls.hostname2 = cls.params2.get_param()
                cls.logger.info(
                    "client_id: {0}, username: {1}, password: {2}, hostname: {3}".format(cls.clientid2, cls.username2,
                                                                                         cls.password2, cls.hostname2))
                cls.mqtt_client2 = MqttClient(host=cls.hostname2, client_id=cls.clientid2, username=cls.username2,
                                             password=cls.password2)

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
        if hasattr(cls, 'mqtt_client2'):
            cls.mqtt_client2.close()
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
    @allure.story("特征同步下发payload的action_id")
    @allure.testcase("FT-HTJK-003-079")
    def test_003079_get_payload_action_id(self):
        self.logger.info(".... test_003079_get_payload_action_id ....")
        re_topic = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey, self.DeviceName)
        re_topic2 = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey2, self.DeviceName2)
        send_topic = "/{0}/{1}/SyncFeatureData/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(re_topic)
                self.mqtt_client.loopstart()
                self.logger.info("device_1 subscribe topic succeed!")
                self.mqtt_client2.subscribe(re_topic2)
                self.mqtt_client2.loopstart()
                self.logger.info("device_2 subscribe topic succeed!")
            with allure.step("teststep2:report feature data"):
                self.logger.info("strat to report feature data.")
                send_payload = {"action_id": "105",
                                "data": {
                                    "device_id": self.device_id,
                                    "feature_info": "123456"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the feature data ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client2.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client2.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                feature_info_payload = msg_payload_dict["data"]["feature_info"]
                allure.attach("Expect action id:", "205")
                allure.attach("Actual action id:", action_id)
                allure.attach("Expect feature_info:", send_payload["data"]["feature_info"])
                allure.attach("Actual feature_info:", feature_info_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                self.logger.info("Actual feature_info:{0}".format(feature_info_payload))
                assert action_id == "205"
                assert send_payload["data"]["feature_info"] == feature_info_payload
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(re_topic)
            self.mqtt_client.loopstop()
            self.mqtt_client2.unsubscribe(re_topic2)
            self.mqtt_client2.loopstop()
            self.logger.info(".... End test_003079_get_payload_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("特征同步下发payload的action_id")
    @allure.testcase("FT-HTJK-003-080")
    def test_003080_get_payload_feature_info(self):
        self.logger.info(".... test_003080_get_payload_feature_info ....")
        re_topic = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey, self.DeviceName)
        re_topic2 = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey2, self.DeviceName2)
        send_topic = "/{0}/{1}/SyncFeatureData/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(re_topic)
                self.mqtt_client.loopstart()
                self.logger.info("device_1 subscribe topic succeed!")
                self.mqtt_client2.subscribe(re_topic2)
                self.mqtt_client2.loopstart()
                self.logger.info("device_2 subscribe topic succeed!")
            with allure.step("teststep2:report feature data"):
                self.logger.info("strat to report feature data.")
                send_payload = {"action_id": "105",
                                "data": {
                                    "device_id": self.device_id,
                                    "feature_info": "123456"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the feature data ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client2.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client2.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                feature_info_payload = msg_payload_dict["data"]["feature_info"]
                allure.attach("Expect action id:", "205")
                allure.attach("Actual action id:", action_id)
                allure.attach("Expect feature_info:", send_payload["data"]["feature_info"])
                allure.attach("Actual feature_info:", feature_info_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                self.logger.info("Actual feature_info:{0}".format(feature_info_payload))
                assert action_id == "205"
                assert send_payload["data"]["feature_info"] == feature_info_payload
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(re_topic)
            self.mqtt_client.loopstop()
            self.mqtt_client2.unsubscribe(re_topic2)
            self.mqtt_client2.loopstop()
            self.logger.info(".... End test_003080_get_payload_feature_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("特征同步下发payload的timestamp")
    @allure.testcase("FT-HTJK-003-081")
    def test_003081_get_payload_timestamp(self):
        self.logger.info(".... test_003081_get_payload_timestamp ....")
        re_topic = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey, self.DeviceName)
        re_topic2 = "/{0}/{1}/SyncFeatureData/Down".format(self.ProductKey2, self.DeviceName2)
        send_topic = "/{0}/{1}/SyncFeatureData/Up".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(re_topic)
                self.mqtt_client.loopstart()
                self.logger.info("device_1 subscribe topic succeed!")
                self.mqtt_client2.subscribe(re_topic2)
                self.mqtt_client2.loopstart()
                self.logger.info("device_2 subscribe topic succeed!")
            with allure.step("teststep2:report feature data"):
                self.logger.info("strat to report feature data.")
                send_payload = {"action_id": "105",
                                "data": {
                                    "device_id": self.device_id,
                                    "feature_info": "123456"},
                                "timestamp": str(get_timestamp())}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the feature data ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client2.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client2.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                feature_info_payload = msg_payload_dict["data"]["feature_info"]
                timestamp_payload = msg_payload_dict["timestamp"]
                local_timestamp = get_timestamp()
                allure.attach("Expect action id:", "205")
                allure.attach("Actual action id:", action_id)
                allure.attach("Expect feature_info:", send_payload["data"]["feature_info"])
                allure.attach("Actual feature_info:", feature_info_payload)
                allure.attach("Expect timestamp:", local_timestamp)
                allure.attach("Actual timestamp:", timestamp_payload)
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                self.logger.info("Actual feature_info:{0}".format(feature_info_payload))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert action_id == "205"
                assert send_payload["data"]["feature_info"] == feature_info_payload
                assert local_timestamp <= int(timestamp_payload) + 5
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(re_topic)
            self.mqtt_client.loopstop()
            self.mqtt_client2.unsubscribe(re_topic2)
            self.mqtt_client2.loopstop()
            self.logger.info(".... End test_003081_get_payload_timestamp ....")
            self.logger.info("")

if __name__ == '__main__':
    pytest.main(['-s', 'test_FeatureData_Sync_Report.py'])
