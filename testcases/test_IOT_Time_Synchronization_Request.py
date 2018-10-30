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


@allure.feature("时间同步请求")
class TestTimeSynchronizationRequest(object):

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
    @allure.story("发送时间同步请求")
    @allure.testcase("FT-HTJK-003-46")
    def test_003046_request_time_synchronization(self):
        self.logger.info(".... test_003046_request_time_synchronization ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                stamp = get_timestamp()
                send_payload = {"action_id": "104", "data": None, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                timestamp_payload = msg_payload_dict["timestamp"]
                local_timestamp = get_timestamp()
                allure.attach("Expect action id:", "204")
                allure.attach("Actual action id:", str(action_id))
                allure.attach("Expect timestamp:", str(local_timestamp))
                allure.attach("Actual timestamp:", str(timestamp_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert action_id == "204"
                assert int(timestamp_payload) == local_timestamp
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003046_request_time_synchronization ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误的action id ,发送时间同步请求")
    @allure.testcase("FT-HTJK-003-47")
    @pytest.mark.parametrize("action_id, result",
                             [('109', []), ('104' * 10, []), ('1.0', []), ('中', []), ('a', []), ('*', []), ('1A', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["action_id(非104)", "action_id(超长值)", "action_id(小数)", "action_id(中文)",
                                  "action_id(字母)", "action_id(特殊字符)", "action_id(数字字母)", "action_id(数字中文)",
                                  "action_id(数字特殊字符)", "action_id(空格)", "action_id(空)"])
    def test_003047_request_time_synchronization_incorrect_action_id(self, action_id, result):
        self.logger.info(".... test_003047_request_time_synchronization_incorrect_action_id ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                stamp = get_timestamp()
                send_payload = {"action_id": action_id, "data": None, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        break
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
            if self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003047_request_time_synchronization_incorrect_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确的timestamp ,发送时间同步请求")
    @allure.testcase("FT-HTJK-003-48")
    @pytest.mark.parametrize("timestamp",
                             [(1), (9999999999)],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_003048_request_time_synchronization_correct_timestamp(self, timestamp):
        self.logger.info(".... test_003048_request_time_synchronization_correct_timestamp ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                # stamp = get_timestamp()
                send_payload = {"action_id": "104", "data": None, "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        self.logger.error("no iot msg received")
                        assert False
                mqtt_msg = self.mqtt_client.rcv_msg.pop()
                msg_payload = mqtt_msg.payload.decode('utf-8')
                msg_payload_dict = json.loads(msg_payload)
                action_id = msg_payload_dict["action_id"]
                timestamp_payload = msg_payload_dict["timestamp"]
                local_timestamp = get_timestamp()
                allure.attach("Expect action id:", "204")
                allure.attach("Actual action id:", str(action_id))
                allure.attach("Expect timestamp:", str(local_timestamp))
                allure.attach("Actual timestamp:", str(timestamp_payload))
                self.logger.info("Actual payload:{0}".format(msg_payload))
                self.logger.info("Actual action id:{0}".format(action_id))
                self.logger.info("Actual timestamp:{0}".format(timestamp_payload))
                assert action_id == "204"
                assert int(timestamp_payload) == local_timestamp
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003048_request_time_synchronization_correct_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误的timestamp ,发送时间同步请求")
    @allure.testcase("FT-HTJK-003-49")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, []), (9223372036854775807, []), (0, []), (-1, []), (-9223372036854775809, []),
                              (9223372036854775808, []), (1.5, []), ('a', []), ('中', []), ('*', []), ('1a', []),
                              ('1中', []), ('1*', []), (' ', []), ('', [])],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_003049_request_time_synchronization_incorrect_timestamp(self, timestamp, result):
        self.logger.info(".... test_003049_request_time_synchronization_incorrect_timestamp ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                # stamp = get_timestamp()
                send_payload = {"action_id": "104", "data": None, "timestamp": str(timestamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        break
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
            if self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003049_request_time_synchronization_incorrect_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少action id ,发送时间同步请求")
    @allure.testcase("FT-HTJK-003-50")
    def test_003050_request_time_synchronization_no_action_id(self):
        self.logger.info(".... test_003050_request_time_synchronization_no_action_id ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                stamp = get_timestamp()
                send_payload = {"data": None, "timestamp": str(stamp)}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        break
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
            if self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003050_request_time_synchronization_no_action_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp ,发送时间同步请求")
    @allure.testcase("FT-HTJK-003-51")
    def test_003051_request_time_synchronization_no_timestamp(self):
        self.logger.info(".... test_003051_request_time_synchronization_no_timestamp ....")
        topic = "/{0}/{1}/Time/Down".format(self.ProductKey, self.DeviceName)
        try:
            with allure.step("teststep1: subscribe the topic."):
                self.mqtt_client.subscribe(topic)
                self.mqtt_client.loopstart()
                self.logger.info("subscribe topic succeed!")
            with allure.step("teststep2:request time synchronization"):
                self.logger.info("strat to request time synchronization.")
                # stamp = get_timestamp()
                send_payload = {"action_id":"104","data": None}
                allure.attach("params value", str(send_payload))
                self.logger.info("params: {0}".format(send_payload))
                send_topic = "/{0}/{1}/Time/Up".format(self.ProductKey, self.DeviceName)
                self.mqtt_client.publish(send_topic, str(send_payload), 1)
                self.logger.info("publish the request ")
            with allure.step("teststep3:assert the payload"):
                start_time = datetime.datetime.now()
                while not self.mqtt_client.rcv_msg:
                    time.sleep(5)
                    end_time = datetime.datetime.now()
                    during = (end_time - start_time).seconds
                    if during > 60:
                        break
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
            if self.mqtt_client.rcv_msg:
                self.mqtt_client.rcv_msg.pop()
            self.mqtt_client.unsubscribe(topic)
            self.mqtt_client.loopstop()
            self.logger.info(".... End test_003051_request_time_synchronization_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_IOT_Time_Synchronization_Request.py'])
