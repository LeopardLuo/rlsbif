#!/usr/bin/env python3
# -*-coding:utf-8-*-

import json
import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.MqttClient import *
from utils.IFFunctions import *


@allure.feature("iot")
class TestMixScenario(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("初始化HTTP客户端。"):
                sv_protocol = cls.config.getItem('server', 'protocol')
                sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, sv_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)
            with allure.step("初始化数据库连接。"):
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

            with allure.step("初始化MQTT客户端"):
                cls.devicename = cls.config.getItem('device', 'd1_devicename')
                cls.secret = cls.config.getItem('device', 'd1_secret')
                cls.productkey = cls.config.getItem('device', 'd1_productkey')
                cls.order_create = cls.config.getItem('iot', 'ServiceOrderPush')
                cls.order_close = cls.config.getItem('iot', 'ServiceOrderClose')
                allure.attach("device params", str((cls.devicename, cls.secret, cls.productkey)))
                cls.logger.info("device params: {}".format((cls.devicename, cls.secret, cls.productkey)))
                params = AliParam(ProductKey=cls.productkey, DeviceName=cls.devicename,
                                  DeviceSecret=cls.secret)
                clientid, username, password, hostname = params.get_param()
                cls.mqttclient = MqttClient(hostname, clientid, username, password)

            with allure.step("delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                cls.logger.info("table: {0}".format(table))
                delete_result = cls.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                cls.logger.info("delete result: {0}".format(delete_result))
        except Exception as e:
            cls.logger.error("Error: there is exception occur:")
            cls.logger.error(e)
            assert False
        finally:
            cls.logger.info("*** End setup class ***")
            cls.logger.info("")

    @allure.step("+++ teardown class +++")
    def teardown_class(cls):
        cls.logger.info("")
        cls.logger.info("*** Start teardown class ***")
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        if hasattr(cls, 'mqttclient'):
            cls.mqttclient.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("blocker")
    @allure.story("本人一次服务单")
    @allure.testcase("FT-HTJK-400-001")
    def test_400001_owner_create_once_service_order(self):
        """ Test subscribe create service order message."""
        self.logger.info(".... Start test_400001_owner_create_once_service_order ....")
        try:
            with allure.step("teststep1: user register."):
                data = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222352", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(data))
                self.logger.info("register params: {0}".format(data))
                register_result = make_register(self.httpclient, data['client_type'], data['client_version'],
                                                data['device_token'], data['imei'], data['code_type'],
                                                data['phone'], data['sms_code'], data['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                token = register_result['token']
                member_id = register_result['user_info']['member_id']

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: identity relative."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                self.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep5: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                system_id = select_result[0][0]
                system_code = select_result[0][2]

            with allure.step("teststep6: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                devices_ids = []
                device_id = ''
                if select_result:
                    device_id = select_result[0][0]
                    devices_ids.append(select_result[0][0])

            with allure.step("teststep7: get features id by user info."):
                user_info = inner_auth(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id = ''
                for item in user_info['features_info']:
                    if item['features_name'] == '本人':
                        features_id = item['features_id']

            with allure.step("teststep8: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep9: create service orders"):
                    order_result = inner_create_service_order(self.httpclient, self.system_id,
                          str(random.randint(1000, 100000)), self.member_id, self.features_id, self.devices_ids, 3,
                          get_timestamp(), 9999999999, 1, random.randint(1000, 100000), 'testunit',
                          'dept1', get_timestamp(), self.logger)
                    allure.attach("create order result", str(order_result))
                    self.logger.info("create order result: {0}".format(order_result))
                    service_order_id = order_result['service_order_id']

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep10: publish service order report."):
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 1, 1, logger=self.logger)
                sleep(3)
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 0, 1, logger=self.logger)

            sleep(10)
            with allure.step("teststep11: get recognize record."):
                records = bs_get_service_order_records(self.httpclient, system_id, service_order_id, system_code, 0, 10,
                                                       get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 2

            with allure.step("teststep12: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 2
                assert status['state'] == 1
                assert len(status['record_ids']) == 2

            with allure.step("teststep13: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep14: close service orders"):
                    close_result = bs_close_service_order(self.httpclient, system_id, service_order_id,
                                                          system_code, 0, get_timestamp(), self.logger)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep15: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 2
                assert status['state'] == 3
                assert len(status['record_ids']) == 2

            with allure.step("teststep16: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'

            with allure.step("teststep17:user logout."):
                logout_result = logout(self.httpclient, member_id, get_timestamp(), self.logger)
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
                assert logout_result
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_400001_owner_create_once_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("本人多次服务单")
    @allure.testcase("FT-HTJK-400-002")
    def test_400002_owner_create_multi_service_order(self):
        """ Test owner create multi times service order."""
        self.logger.info(".... Start test_400002_owner_create_multi_service_order ....")
        try:
            with allure.step("teststep1: user register."):
                data = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222353", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(data))
                self.logger.info("register params: {0}".format(data))
                register_result = make_register(self.httpclient, data['client_type'], data['client_version'],
                                                data['device_token'], data['imei'], data['code_type'],
                                                data['phone'], data['sms_code'], data['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                token = register_result['token']
                member_id = register_result['user_info']['member_id']

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: identity relative."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                self.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep5: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                system_id = select_result[0][0]
                system_code = select_result[0][2]

            with allure.step("teststep6: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                devices_ids = []
                device_id = ''
                if select_result:
                    device_id = select_result[0][0]
                    devices_ids.append(select_result[0][0])

            with allure.step("teststep7: get features id by user info."):
                user_info = inner_auth(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id = ''
                for item in user_info['features_info']:
                    if item['features_name'] == '本人':
                        features_id = item['features_id']

            with allure.step("teststep8: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep9: create service orders"):
                    order_result = inner_create_service_order(self.httpclient, self.system_id,
                                                              str(random.randint(1000, 100000)), self.member_id,
                                                              self.features_id, self.devices_ids, 3,
                                                              get_timestamp(), 9999999999, 10,
                                                              random.randint(1000, 100000), 'testunit',
                                                              'dept1', get_timestamp(), self.logger)
                    allure.attach("create order result", str(order_result))
                    self.logger.info("create order result: {0}".format(order_result))
                    service_order_id = order_result['service_order_id']

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep10: publish service order report."):
                for i in range(10):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep11: get recognize record."):
                records = bs_get_service_order_records(self.httpclient, system_id, service_order_id, system_code, 0, 10,
                                                       get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 20

            with allure.step("teststep12: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 20
                assert status['state'] == 1
                assert len(status['record_ids']) == 20

            with allure.step("teststep13: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep14: close service orders"):
                    close_result = bs_close_service_order(self.httpclient, system_id, service_order_id,
                                                          system_code, 0, get_timestamp(), self.logger)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep15: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 20
                assert status['state'] == 3
                assert len(status['record_ids']) == 20

            with allure.step("teststep16: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'

            with allure.step("teststep17:user logout."):
                logout_result = logout(self.httpclient, member_id, get_timestamp(), self.logger)
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
                assert logout_result
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_400002_owner_create_multi_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人一次服务单")
    @allure.testcase("FT-HTJK-400-003")
    def test_400003_relative_create_once_service_order(self):
        """ Test subscribe create service order message."""
        self.logger.info(".... Start test_400003_relative_create_once_service_order ....")
        try:
            with allure.step("teststep1: user register."):
                data = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222351", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(data))
                self.logger.info("register params: {0}".format(data))
                register_result = make_register(self.httpclient, data['client_type'], data['client_version'],
                                                data['device_token'], data['imei'], data['code_type'],
                                                data['phone'], data['sms_code'], data['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                token = register_result['token']
                member_id = register_result['user_info']['member_id']

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: identity relative."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                self.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep5: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                system_id = select_result[0][0]
                system_code = select_result[0][2]

            with allure.step("teststep6: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                devices_ids = []
                device_id = ''
                if select_result:
                    device_id = select_result[0][0]
                    devices_ids.append(select_result[0][0])

            with allure.step("teststep7: get features id by user info."):
                user_info = inner_auth(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id = ''
                for item in user_info['features_info']:
                    if item['features_name'] == 'kuli1':
                        features_id = item['features_id']

            with allure.step("teststep8: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep9: create service orders"):
                    order_result = inner_create_service_order(self.httpclient, self.system_id,
                                                              str(random.randint(1000, 100000)), self.member_id,
                                                              self.features_id, self.devices_ids, 3,
                                                              get_timestamp(), 9999999999, 1,
                                                              random.randint(1000, 100000), 'testunit',
                                                              'dept1', get_timestamp(), self.logger)
                    allure.attach("create order result", str(order_result))
                    self.logger.info("create order result: {0}".format(order_result))
                    service_order_id = order_result['service_order_id']

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep10: publish service order report."):
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 1, 1, logger=self.logger)
                sleep(3)
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 0, 1, logger=self.logger)

            sleep(10)
            with allure.step("teststep11: get recognize record."):
                records = bs_get_service_order_records(self.httpclient, system_id, service_order_id, system_code, 0, 10, get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 2

            with allure.step("teststep12: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code, get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 2
                assert status['state'] == 1
                assert len(status['record_ids']) == 2

            with allure.step("teststep13: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep14: close service orders"):
                    close_result = bs_close_service_order(self.httpclient, system_id, service_order_id,
                                                           system_code, 0, get_timestamp(), self.logger)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep15: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code, get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 2
                assert status['state'] == 3
                assert len(status['record_ids']) == 2

            with allure.step("teststep16: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'

            with allure.step("teststep17:user logout."):
                logout_result = logout(self.httpclient, member_id, get_timestamp(), self.logger)
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
                assert logout_result
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_400003_relative_create_once_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人多次服务单")
    @allure.testcase("FT-HTJK-400-004")
    def test_400004_relative_create_multi_service_order(self):
        """ Test relative create multi times service order."""
        self.logger.info(".... Start test_400004_relative_create_multi_service_order ....")
        try:
            with allure.step("teststep1: user register."):
                data = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222354", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(data))
                self.logger.info("register params: {0}".format(data))
                register_result = make_register(self.httpclient, data['client_type'], data['client_version'],
                                                data['device_token'], data['imei'], data['code_type'],
                                                data['phone'], data['sms_code'], data['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                token = register_result['token']
                member_id = register_result['user_info']['member_id']

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: identity relative."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                self.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep5: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                system_id = select_result[0][0]
                system_code = select_result[0][2]

            with allure.step("teststep6: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                devices_ids = []
                device_id = ''
                if select_result:
                    device_id = select_result[0][0]
                    devices_ids.append(select_result[0][0])

            with allure.step("teststep7: get features id by user info."):
                user_info = inner_auth(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id = ''
                for item in user_info['features_info']:
                    if item['features_name'] == 'kuli1':
                        features_id = item['features_id']

            with allure.step("teststep8: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep9: create service orders"):
                    order_result = inner_create_service_order(self.httpclient, self.system_id,
                                                              str(random.randint(1000, 100000)), self.member_id,
                                                              self.features_id, self.devices_ids, 3,
                                                              get_timestamp(), 9999999999, 10,
                                                              random.randint(1000, 100000), 'testunit',
                                                              'dept1', get_timestamp(), self.logger)
                    allure.attach("create order result", str(order_result))
                    self.logger.info("create order result: {0}".format(order_result))
                    service_order_id = order_result['service_order_id']

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep10: publish service order report."):
                for i in range(10):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep11: get recognize record."):
                records = bs_get_service_order_records(self.httpclient, system_id, service_order_id, system_code, 0, 10,
                                                       get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 20

            with allure.step("teststep12: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 20
                assert status['state'] == 1
                assert len(status['record_ids']) == 20

            with allure.step("teststep13: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep14: close service orders"):
                    close_result = bs_close_service_order(self.httpclient, system_id, service_order_id,
                                                          system_code, 0, get_timestamp(), self.logger)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while not self.mqttclient.rcv_msg and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep15: get service order status."):
                status = bs_get_service_order_status(self.httpclient, system_id, service_order_id, system_code,
                                                     get_timestamp(), self.logger)
                self.logger.info("Service order Status: {0}".format(status))
                assert status['already_count'] == 20
                assert status['state'] == 3
                assert len(status['record_ids']) == 20

            with allure.step("teststep16: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'

            with allure.step("teststep17:user logout."):
                logout_result = logout(self.httpclient, member_id, get_timestamp(), self.logger)
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
                assert logout_result
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_400004_relative_create_multi_service_order ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_scenario.py'])
    pytest.main(['-s', 'test_scenario.py::TestMixScenario::test_400004_relative_create_multi_service_order'])
