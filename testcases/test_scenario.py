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


@pytest.mark.IOT
@allure.feature("复合场景-识别")
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
                cls.sv_protocol = cls.config.getItem('server', 'protocol')
                cls.sv_host = cls.config.getItem('server', 'host')
                cls.sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(cls.sv_protocol, cls.sv_host, cls.sv_port)
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
            with allure.step("初始化MQTT客户端2"):
                cls.devicename2 = cls.config.getItem('device', 'd2_devicename')
                cls.secret2 = cls.config.getItem('device', 'd2_secret')
                cls.productkey2 = cls.config.getItem('device', 'd2_productkey')
                allure.attach("device params", str((cls.devicename2, cls.secret2, cls.productkey2)))
                cls.logger.info("device params: {}".format((cls.devicename2, cls.secret2, cls.productkey2)))
                params2 = AliParam(ProductKey=cls.productkey2, DeviceName=cls.devicename2,
                                  DeviceSecret=cls.secret2)
                clientid2, username2, password2, hostname2 = params2.get_param()
                cls.mqttclient2 = MqttClient(hostname2, clientid2, username2, password2)

            with allure.step("delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                cls.logger.info("table: {0}".format(table))
                delete_result = cls.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                cls.logger.info("delete result: {0}".format(delete_result))

            with allure.step("teststep: user register."):
                data = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(data))
                cls.logger.info("register params: {0}".format(data))
                register_result = make_register(cls.httpclient, data['client_type'], data['client_version'],
                                                data['device_token'], data['imei'], data['code_type'],
                                                data['phone'], data['sms_code'], data['timestamp'], cls.logger)
                allure.attach("register result", str(register_result))
                cls.logger.info("register result: {0}".format(register_result))
                cls.token = register_result['token']
                cls.member_id = register_result['user_info']['member_id']
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)

            with allure.step("teststep2: user feature."):
                identity_result = user_myfeature(cls.httpclient, cls.member_id, 'face2.jpg',
                                                 get_timestamp(), cls.logger, '本人')
                allure.attach("upload user feature result", "{0}".format(identity_result))
                cls.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(cls.httpclient, cls.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                cls.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: identity relative."):
                identity_result1 = identity_other(cls.httpclient, cls.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), cls.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                cls.logger.info("identity relative result: {0}".format(identity_result1))
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
        with allure.step("teststep: user logout."):
            logout_result = logout(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
            allure.attach("logout result", str(logout_result))
            cls.logger.info("logout result: {0}".format(logout_result))
        with allure.step("teststep: delete user features"):
            table = 'mem_features'
            condition = ("member_id", cls.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            cls.logger.info("")
            cls.logger.info("table: {0}, condition: {1}".format(table, condition))
            select_result = cls.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(select_result))
            cls.logger.info("delete result: {0}".format(select_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        if hasattr(cls, 'mqttclient'):
            cls.mqttclient.close()
        if hasattr(cls,"mqttclient2"):
            cls.mqttclient2.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("blocker")
    @allure.story("本人一次服务单")
    @allure.testcase("FT-HTJK-400-001")
    def test_400001_owner_create_once_service_order(self):
        """ Test subscribe create service order message."""
        self.logger.info(".... Start test_400001_owner_create_once_service_order ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get devices id"):
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

            with allure.step("teststep10: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep11: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                                  [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = r_orderlist[0]["service_order_id"]

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

            with allure.step("teststep12: publish service order report."):
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 1, 1, logger=self.logger)
                sleep(3)
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 0, 1, logger=self.logger)

            sleep(10)
            with allure.step("teststep13: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 10, timestamp=get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 2

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 2
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
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

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 2
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400001_owner_create_once_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("本人多次服务单")
    @allure.testcase("FT-HTJK-400-002")
    def test_400002_owner_create_multi_service_order(self):
        """ Test owner create multi times service order."""
        self.logger.info(".... Start test_400002_owner_create_multi_service_order ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get devices id"):
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

            with allure.step("teststep10: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep11: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                                  [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = r_orderlist[0]["service_order_id"]

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

            with allure.step("teststep12: publish service order report."):
                for i in range(5):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep13: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 10, timestamp=get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 10

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 10
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
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

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 10
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400002_owner_create_multi_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人一次服务单")
    @allure.testcase("FT-HTJK-400-003")
    def test_400003_relative_create_once_service_order(self):
        """ Test subscribe create service order message."""
        self.logger.info(".... Start test_400003_relative_create_once_service_order ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get features id by user info."):
                user_info = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(), logger=self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id1 = user_info[0]['features_id']

            with allure.step("teststep10: get devices id"):
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

            with allure.step("teststep11: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep12: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id,
                                                                  sku_id, [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                    with allure.step("邀请访客下单"):
                        r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                                                                        "kuli1", time.strftime("%Y-%m-%d"),
                                                                        "2021-02-10", "relate_face.jpg", self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = None
                        for order in r_orderlist:
                            if order['features_name'] == 'kuli1':
                                service_order_id = order["service_order_id"]

                end_time = int(time.time())
                during = end_time - start_time
                while len(self.mqttclient.rcv_msg)<2 and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    if len(self.mqttclient.rcv_msg)<2:
                        self.logger.error("device1 received message less than 2!")
                        assert False
                    while self.mqttclient.rcv_msg:
                        msg = self.mqttclient.rcv_msg.pop()
                        payload = json.loads(msg.payload, encoding='utf-8')
                        self.logger.info("message payload: {}".format(payload))
                    #assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep13: publish service order report."):
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 1, 1, logger=self.logger)
                sleep(3)
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               device_id, 0, 1, logger=self.logger)

            sleep(10)
            with allure.step("teststep13: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 10, timestamp=get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 2

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 2
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
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

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 2
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                self.mqttclient.clear()
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Time sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400003_relative_create_once_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人多次服务单")
    @allure.testcase("FT-HTJK-400-004")
    def test_400004_relative_create_multi_service_order(self):
        """ Test relative create multi times service order."""
        self.logger.info(".... Start test_400004_relative_create_multi_service_order ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get features id by user info."):
                user_info = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(), logger=self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id1 = user_info[0]['features_id']

            with allure.step("teststep10: get devices id"):
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

            with allure.step("teststep11: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep12: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id,
                                                                  sku_id, [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                    with allure.step("邀请访客下单"):
                        r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                                                                        "kuli1", time.strftime("%Y-%m-%d"),
                                                                        "2021-02-10", "relate_face.jpg", self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = None
                        for order in r_orderlist:
                            if order['features_name'] == 'kuli1':
                                service_order_id = order["service_order_id"]

                end_time = int(time.time())
                during = end_time - start_time
                while len(self.mqttclient.rcv_msg)<2 and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                if self.mqttclient.rcv_msg:
                    if len(self.mqttclient.rcv_msg)<2:
                        self.logger.error("device1 received message less than 2!")
                        assert False
                    while self.mqttclient.rcv_msg:
                        msg = self.mqttclient.rcv_msg.pop()
                        payload = json.loads(msg.payload, encoding='utf-8')
                        self.logger.info("message payload: {}".format(payload))
                    #assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep13: publish service order report."):
                for i in range(5):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep14: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 20, timestamp=get_timestamp(), logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 10

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 10
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
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

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 10
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                self.mqttclient.clear()
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("Tiime sync message payload: {}".format(payload))
                assert payload['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400004_relative_create_multi_service_order ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("本人多次服务单-不同设备")
    @allure.testcase("FT-HTJK-400-005")
    def test_400005_owner_create_multi_service_order_different_devices(self):
        """ Test owner create multi times service order,different devices."""
        self.logger.info(".... Start test_400005_owner_create_multi_service_order_different_devices ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
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

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                condition2 = ("iot_device_name", self.devicename2)
                allure.attach("table name and condition", "{0},{1}".format(table, condition2))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition2))
                select_result2 = self.mysql.execute_select_condition(table, condition2)
                allure.attach("query result", str(select_result2))
                self.logger.info("query result: {0}".format(select_result2))
                devices_ids = []
                device_id = ''
                device_id2 = ''
                if select_result and select_result2:
                    device_id = select_result[0][0]
                    device_id2 = select_result2[0][0]
                    devices_ids.append(select_result[0][0])
                    devices_ids.append(select_result2[0][0])

            with allure.step("teststep10: subscribe service order create."):
                self.mqttclient2.loopstart()
                time.sleep(5)
                self.mqttclient2.loopstop()
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                topic2 = "/{0}/{1}/{2}".format(self.productkey2, self.devicename2, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient2.subscribe(topic2, 1)
                self.mqttclient2.loopstart()
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient.clear()
                self.mqttclient2.clear()
                start_time = int(time.time())

                with allure.step("teststep11: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                                  [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                               timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = r_orderlist[0]["service_order_id"]

                end_time = int(time.time())
                during = end_time - start_time
                while (not self.mqttclient.rcv_msg or not self.mqttclient2.rcv_msg) and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                self.mqttclient2.loopstop()
                self.mqttclient2.unsubscribe(topic2)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("device1 message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.info("Fail: Cannot get the create service order message from device1.")
                    assert False
                if self.mqttclient2.rcv_msg:
                    msg = self.mqttclient2.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("device2 message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.info("Fail: Cannot get the create service order message from device2.")
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep12: publish service order report."):
                for i in range(4):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient2, self.productkey2, self.devicename2, service_order_id,
                                                   device_id2, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep13: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 10, timestamp=get_timestamp(),
                                                     logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 8

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 8
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                topic2 = "/{0}/{1}/{2}".format(self.productkey2, self.devicename2, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.logger.info("topic: {0}".format(topic2))
                self.mqttclient2.subscribe(topic2, 1)
                self.mqttclient2.loopstart()
                self.mqttclient.clear()
                self.mqttclient2.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while (not self.mqttclient.rcv_msg) and (not self.mqttclient2.rcv_msg) and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                self.mqttclient2.loopstop()
                self.mqttclient2.unsubscribe(topic2)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("device1 message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device1 has not received iot message")
                    assert False
                if self.mqttclient2.rcv_msg:
                    msg = self.mqttclient2.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("device2 message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device2 has not received iot message")
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 8
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                self.mqttclient.clear()
                self.mqttclient2.clear()
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("device1 time sync message payload: {}".format(payload))
                payload2 = iot_publish_SyncTime(self.mqttclient2, self.productkey2, self.devicename2, 1, logger=self.logger)
                self.logger.info("device2 time sync message payload: {}".format(payload2))
                assert payload['action_id'] == '204'
                assert payload2['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400005_owner_create_multi_service_order_different_devices ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人多次服务单-不同设备")
    @allure.testcase("FT-HTJK-400-006")
    def test_400006_relative_create_multi_service_order_different_devices(self):
        """ Test relative create multi times service order different devices."""
        self.logger.info(".... Start test_400006_relative_create_multi_service_order_different_devices ....")
        try:
            with allure.step("teststep5: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
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

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get features id by user info."):
                user_info = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                    logger=self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id1 = user_info[0]['features_id']

            with allure.step("teststep10: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", self.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                condition2 = ("iot_device_name", self.devicename2)
                allure.attach("table name and condition", "{0},{1}".format(table, condition2))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition2))
                select_result2 = self.mysql.execute_select_condition(table, condition2)
                allure.attach("query result", str(select_result2))
                self.logger.info("query result: {0}".format(select_result2))
                devices_ids = []
                device_id = ''
                device_id2 = ''
                if select_result:
                    device_id = select_result[0][0]
                    device_id2 = select_result2[0][0]
                    devices_ids.append(select_result[0][0])
                    devices_ids.append(select_result2[0][0])

            with allure.step("teststep11: subscribe service order create."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_create)
                topic2 = "/{0}/{1}/{2}".format(self.productkey2, self.devicename2, self.order_create)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient2.subscribe(topic2, 1)
                self.mqttclient2.loopstart()
                self.mqttclient.clear()
                self.mqttclient2.clear()
                start_time = int(time.time())

                with allure.step("teststep12: create service orders"):
                    with allure.step("初始化HTTP客户端。"):
                        h5_port = self.config.getItem('h5', 'port')
                        baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                        allure.attach("baseurl", str(baseurl))
                        self.logger.info("baseurl: " + baseurl)
                        httpclient1 = HTTPClient(baseurl)
                    with allure.step("连接H5主页"):
                        r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                        allure.attach("homeindex", str(r_homeindex))
                        self.logger.info("homeindex: " + str(r_homeindex))
                        assert not r_homeindex
                    with allure.step("本人申请下单"):
                        r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id,
                                                                  sku_id, [owner_feautreid], "2010-2-4", "2038-02-11",
                                                                  self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                    with allure.step("邀请访客下单"):
                        r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                                                                        "kuli1", time.strftime("%Y-%m-%d"),
                                                                        "2021-02-10", "relate_face.jpg", self.logger)
                        allure.attach("apply result", str(r_applyresult1))
                        self.logger.info("apply result: " + str(r_applyresult1))
                        assert r_applyresult1
                    with allure.step("获取服务单号"):
                        r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                               timestamp=get_timestamp(), logger=self.logger)
                        self.logger.info("service order list: " + str(r_orderlist))
                        service_order_id = None
                        for order in r_orderlist:
                            if order['features_name'] == 'kuli1':
                                service_order_id = order["service_order_id"]

                end_time = int(time.time())
                during = end_time - start_time
                while ( len(self.mqttclient.rcv_msg)<2 or len(self.mqttclient2.rcv_msg)<2) and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                self.mqttclient2.loopstop()
                self.mqttclient2.unsubscribe(topic2)
                if self.mqttclient.rcv_msg:
                    if len(self.mqttclient.rcv_msg)<2:
                        self.logger.error("device1 received message less than 2!")
                        assert False
                    while self.mqttclient.rcv_msg:
                        msg = self.mqttclient.rcv_msg.pop()
                        payload = json.loads(msg.payload, encoding='utf-8')
                        self.logger.info("device1 message payload: {}".format(payload))
                    # assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device1 has not received iot message")
                    assert False
                if self.mqttclient2.rcv_msg:
                    if len(self.mqttclient2.rcv_msg)<2:
                        self.logger.error("device2 received message less than 2!")
                        assert False
                    while self.mqttclient2.rcv_msg:
                        msg = self.mqttclient2.rcv_msg.pop()
                        payload = json.loads(msg.payload, encoding='utf-8')
                        self.logger.info("device2 message payload: {}".format(payload))
                    # assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device2 has not received iot message")
                    assert False
                self.logger.info("MQTT receive service order create finished.")

            with allure.step("teststep13: publish service order report."):
                for i in range(4):
                    self.logger.info("")
                    self.logger.info("Publish service order report {} times.".format(i))
                    iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                                   device_id, 1, 1, logger=self.logger)
                    sleep(3)
                    iot_publish_ServiceOrderReport(self.mqttclient2, self.productkey2, self.devicename2, service_order_id,
                                                   device_id2, 0, 1, logger=self.logger)
                    sleep(3)

            sleep(10)
            with allure.step("teststep14: get recognize record."):
                records = get_recognized_record_list(self.httpclient, self.member_id, 0, 20, timestamp=get_timestamp(),
                                                     logger=self.logger)
                self.logger.info("Recognize records: {0}".format(records))
                assert len(records['data']) == 8

            with allure.step("teststep14: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 20, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order list: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 8
                assert r_orderlist[0]['state'] == 1

            with allure.step("teststep15: subscribe service order close."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.order_close)
                topic2 = "/{0}/{1}/{2}".format(self.productkey2, self.devicename2, self.order_close)
                self.logger.info("topic: {0}".format(topic))
                self.logger.info("topic: {0}".format(topic2))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                self.mqttclient2.subscribe(topic2, 1)
                self.mqttclient2.loopstart()
                self.mqttclient.clear()
                self.mqttclient2.clear()
                start_time = int(time.time())

                with allure.step("teststep16: close service orders"):
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_result = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id)
                    allure.attach("close order result", str(close_result))
                    self.logger.info("close order result: {0}".format(close_result))
                    assert close_result

                end_time = int(time.time())
                during = end_time - start_time
                while (not self.mqttclient.rcv_msg) and (self.mqttclient2.rcv_msg) and during < 60:
                    sleep(5)
                    end_time = int(time.time())
                    during = end_time - start_time
                self.mqttclient.loopstop()
                self.mqttclient.unsubscribe(topic)
                self.mqttclient2.loopstop()
                self.mqttclient2.unsubscribe(topic2)
                if self.mqttclient.rcv_msg:
                    msg = self.mqttclient.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device1 has not received iot message")
                    assert False
                if self.mqttclient2.rcv_msg:
                    msg = self.mqttclient2.rcv_msg.pop()
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['action_id'] == '203'
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    self.logger.error("Failed:device2 has not received iot message")
                    assert False
                self.logger.info("MQTT receive service order close finished.")

            with allure.step("teststep17: get service order status."):
                r_orderlist = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                       logger=self.logger)
                self.logger.info("Service order Status: {0}".format(r_orderlist))
                assert r_orderlist[0]['already_count'] == 8
                assert r_orderlist[0]['state'] == 2

            with allure.step("teststep18: subscribe sync time."):
                self.mqttclient.clear()
                self.mqttclient2.clear()
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("device1 Time sync message payload: {}".format(payload))
                payload2 = iot_publish_SyncTime(self.mqttclient2, self.productkey2, self.devicename2, 1, logger=self.logger)
                self.logger.info("device2 Time sync message payload: {}".format(payload2))
                assert payload['action_id'] == '204'
                assert payload2['action_id'] == '204'
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete mem order records"):
                table = 'mem_order_record'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_400006_relative_create_multi_service_order_different_devices ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_scenario.py'])
    # pytest.main(['-s', 'test_scenario.py::TestMixScenario::test_400005_owner_create_multi_service_order_different_devices'])
