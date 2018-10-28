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
    @allure.story("正常设备特征同步上报")
    @allure.testcase("FT-HTJK-003-068")
    def test_003068_report_feature_data_synchronization(self):
        self.logger.info(".... test_003068_report_feature_data_synchronization ....")
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
            self.logger.info(".... End test_003068_report_feature_data_synchronization ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误的action_id，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-069")
    @pytest.mark.parametrize("action_id, result",
                             [('109', []), ('105' * 10, []), ('1.0', []), ('中', []), ('a', []), ('*', []), ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["action_id(非105)", "action_id(超长值)", "action_id(小数)", "action_id(中文)",
                                  "action_id(字母)", "action_id(特殊字符)", "action_id(数字字母)", "action_id(数字中文)",
                                  "action_id(数字特殊字符)", "action_id(空格)", "action_id(空)"])
    def test_003069_report_feature_data_synchronization_incorrect_action_id(self, action_id, result):
        self.logger.info(".... test_003069_report_feature_data_synchronization_incorrect_action_id ....")
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
                send_payload = {"action_id": action_id,
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", result)
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
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
            self.logger.info(".... End test_003069_report_feature_data_synchronization_incorrect_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误的device_id，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-070")
    @pytest.mark.parametrize("device_id, result",
                             [('33912662580592640', []), ('100' * 10, []), ('1.5', []), ('中', []), ('a', []), ('*', []),
                              ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["device_id(非增加设备id值)", "device_id(超长值)", "device_id(小数)", "device_id(中文)",
                                  "device_id(字母)", "device_id(特殊字符)", "device_id(数字字母)", "device_id(数字中文)",
                                  "device_id(数字特殊字符)", "device_id(空格)", "device_id(空)"])
    def test_003070_report_feature_data_synchronization_incorrect_device_id(self, device_id, result):
        self.logger.info(".... test_003070_report_feature_data_synchronization_incorrect_device_id ....")
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
                                    "device_id": device_id,
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", result)
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
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
            self.logger.info(".... End test_003070_report_feature_data_synchronization_incorrect_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正常feature_info，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-071")
    @pytest.mark.parametrize("feature_info",
                             [('{"action_id":123,"data":"abc","timestamp":123456}'), ('11112'), ('abcd')],
                             ids=["feature_info(JSON字符串)", "feature_info(数字)", "feature_info(字母)"])
    def test_003071_report_feature_data_synchronization_correct_feature_info(self,feature_info):
        self.logger.info(".... test_003071_report_feature_data_synchronization_correct_feature_info ....")
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
                                    "feature_info": feature_info},
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
            self.logger.info(".... End test_003071_report_feature_data_synchronization_correct_feature_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误的feature_info，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-072")
    @pytest.mark.parametrize("feature_info, result",
                             [ ('中', []), ('*', []),('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["device_id(中文)", "device_id(特殊字符)", "device_id(数字中文)",
                                  "device_id(数字特殊字符)", "device_id(空格)", "device_id(空)"])
    def test_003072_report_feature_data_synchronization_incorrect_feature_info(self, feature_info, result):
        self.logger.info(".... test_003072_report_feature_data_synchronization_incorrect_feature_info ....")
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
                                    "feature_info": feature_info},
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", result)
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
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
            self.logger.info(".... End test_003072_report_feature_data_synchronization_incorrect_feature_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置正常timestamp，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-073")
    @pytest.mark.parametrize("timestamp",
                             [(1), (9999999999)],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_003073_report_feature_data_synchronization_correct_timestamp(self, timestamp):
        self.logger.info(".... test_003073_report_feature_data_synchronization_correct_timestamp ....")
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
                                "timestamp": str(timestamp)}
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
            self.logger.info(".... End test_003073_report_feature_data_synchronization_correct_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("设置错误的timestamp，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-074")
    @pytest.mark.parametrize("timestamp, result",
                             [(9223372036854775807, []), (0, []), (-1, []), (-9223372036854775809, []),
                              (9223372036854775808, []), (1.5, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_003074_report_feature_data_synchronization_incorrect_timestamp(self, timestamp, result):
        self.logger.info(".... test_003074_report_feature_data_synchronization_incorrect_timestamp ....")
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
                                "timestamp": str(timestamp)}
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", result)
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == result
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
            self.logger.info(".... End test_003074_report_feature_data_synchronization_incorrect_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少action_id，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-075")
    def test_003075_report_feature_data_synchronization_no_action_id(self):
        self.logger.info(".... test_003075_report_feature_data_synchronization_no_action_id ....")
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
                send_payload = {
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", [])
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
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
            self.logger.info(".... End test_003075_report_feature_data_synchronization_no_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_id，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-076")
    def test_003076_report_feature_data_synchronization_no_device_id(self):
        self.logger.info(".... test_003076_report_feature_data_synchronization_no_device_id ....")
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
                send_payload = {   "action_id": "105",
                    "data": {
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", [])
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
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
            self.logger.info(".... End test_003076_report_feature_data_synchronization_no_device_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少feature_info，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-077")
    def test_003077_report_feature_data_synchronization_no_feature_info(self):
        self.logger.info(".... test_003077_report_feature_data_synchronization_no_feature_info ....")
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
                                    "device_id": self.device_id},
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", [])
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
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
            self.logger.info(".... End test_003077_report_feature_data_synchronization_no_feature_info ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp，设备特征同步上报")
    @allure.testcase("FT-HTJK-003-078")
    def test_003078_report_feature_data_synchronization_no_timestamp(self):
        self.logger.info(".... test_003078_report_feature_data_synchronization_no_timestamp ....")
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
                                "feature_info": "123456"}}
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
                        break
                mqtt_msg = self.mqtt_client2.rcv_msg
                allure.attach("Expect payload:", [])
                allure.attach("Actual payload:", mqtt_msg)
                self.logger.info("Actual payload:{0}".format(mqtt_msg))
                assert mqtt_msg == []
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
            self.logger.info(".... End test_003078_report_feature_data_synchronization_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_FeatureData_Sync_Report.py'])
