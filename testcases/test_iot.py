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
class TestIOTSubscribe(object):

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
                cls.tp = cls.config.getItem('iot', 'ServiceOrderPush')
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

            with allure.step("user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222351", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                cls.logger.info("register params: {0}".format(json))
                register_result = make_register(cls.httpclient, json['client_type'], json['client_version'],
                                       json['device_token'], json['imei'], json['code_type'],
                                        json['phone'], json['sms_code'], json['timestamp'], cls.logger)
                allure.attach("register result", str(register_result))
                cls.logger.info("register result: {0}".format(register_result))
                cls.token = register_result['token']
                cls.member_id = register_result['user_info']['member_id']

            with allure.step("teststep: identity user."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_identity(cls.httpclient, cls.member_id, 'fore2.jpg', 'back2.jpg', 'face2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                cls.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep: identity relative."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result1 = identity_other(cls.httpclient, cls.member_id, 'kuli1', 'relate_face.jpg',
                                                  'relate_com.jpg',
                                                  get_timestamp(), cls.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                cls.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep: get business token."):
                cls.httpclient.update_header({"authorization": cls.token})
                business_result = h5_get_business_token(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
                allure.attach("business token", str(business_result))
                cls.logger.info("business token: {}".format(business_result))
                business_token = business_result['business_token']

            with allure.step("teststep: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.system_id = select_result[0][0]
                cls.system_code = select_result[0][2]

            with allure.step("teststep: get devices id"):
                table = 'iot_releationship'
                condition = ("iot_device_name", cls.devicename)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.devices_ids = []
                if select_result:
                    cls.device_id = select_result[0][0]
                    cls.devices_ids.append(select_result[0][0])

            with allure.step("teststep: get features id by user info."):
                user_info = bs_get_user_info(cls.httpclient, cls.system_id, cls.member_id, business_token,
                                             get_timestamp(), cls.logger)
                allure.attach("features data list", "{0}".format(user_info))
                cls.logger.info("features data list: {0}".format(user_info))
                cls.features_id = ''
                for item in user_info['features_info']:
                    if item['features_name'] == 'kuli1':
                        cls.features_id = item['features_id']
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
        with allure.step("user logout."):
            cls.httpclient.update_header({"authorization": cls.token})
            logout_result = logout(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
            cls.httpclient.update_header({"authorization": None})
            allure.attach("logout result", str(logout_result))
            cls.logger.info("logout result: {0}".format(logout_result))
        with allure.step("teststep: delete user identity record"):
            table = 'mem_features'
            condition = ("member_id", cls.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            cls.logger.info("")
            cls.logger.info("table: {0}, condition: {1}".format(table, condition))
            select_result = cls.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(select_result))
            cls.logger.info("delete result: {0}".format(select_result))
        with allure.step("delete service order records"):
            table = 'bus_service_order'
            condition = ("member_id", cls.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            cls.logger.info("")
            cls.logger.info("table: {0}, condition: {1}".format(table, condition))
            delete_result = cls.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            cls.logger.info("delete result: {0}".format(delete_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        if hasattr(cls, 'mqttclient'):
            cls.mqttclient.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("blocker")
    @allure.story("订阅创建服务单")
    @allure.testcase("FT-HTJK-xxx-001")
    def test_xxx001_subscribe_create_service_order(self):
        """ Test subscribe create service order message."""
        self.logger.info(".... Start test_xxx001_subscribe_create_service_order ....")
        try:
            with allure.step("teststep1: subscribe service order."):
                topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, self.tp)
                self.logger.info("topic: {0}".format(topic))
                self.mqttclient.subscribe(topic, 1)
                self.mqttclient.loopstart()
                start_time = int(time.time())

                with allure.step("teststep: create service orders"):
                    self.httpclient.update_header({"authorization": self.token})
                    order_result = h5_create_service_order(self.httpclient, self.system_id,
                                                           str(random.randint(1000, 100000)), self.member_id,
                                                           self.system_code, self.features_id, self.devices_ids, 3,
                                                           get_timestamp(), 9999999999, 10, 'testunit',
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
                    # str1 = str(msg.payload, encoding="utf-8")
                    # payload = eval(str1)
                    payload = json.loads(msg.payload, encoding='utf-8')
                    self.logger.info("message payload: {}".format(payload))
                    assert payload['data']['service_order_id'] == str(service_order_id)
                else:
                    assert False
                self.logger.info("MQTT receive service order finished.")

            with allure.step("teststep2: publish service order report."):
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               self.device_id, 1, 1, logger=self.logger)
                sleep(3)
                iot_publish_ServiceOrderReport(self.mqttclient, self.productkey, self.devicename, service_order_id,
                                               self.device_id, 0, 1, logger=self.logger)
                # topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, "ServiceOrderReport")
                # in_payload = {
                #     "action_id": "100",
                #     "data": {
                #         "service_order_id": str(service_order_id),
                #         "device_id": str(self.device_id),
                #         "in_out": "1",
                #         "exrea": "",
                #     },
                #     "timestamp": str(get_timestamp())
                # }
                # self.logger.info("topic: {0}".format(topic))
                # self.logger.info("in payload: {0}".format(in_payload))
                # self.mqttclient.publish(topic, str(in_payload), 1)
                # sleep(5)
                # out_payload = {
                #     "action_id": "100",
                #     "data": {
                #         "service_order_id": str(service_order_id),
                #         "device_id": str(self.device_id),
                #         "in_out": "0",
                #         "exrea": "",
                #     },
                #     "timestamp": str(get_timestamp())
                # }
                # self.logger.info("out payload: {0}".format(out_payload))
                # self.mqttclient.publish(topic, str(out_payload), 1)

            sleep(10)
            with allure.step("teststep3: get recognize record."):
                records = bs_get_service_order_records(self.httpclient, self.system_id, service_order_id, self.system_code, 0, 10, get_timestamp(), logger=self.logger)
                self.logger.info("records: {0}".format(records))
                print("data num: {}".format(len(records['data'])))

            with allure.step("teststep1: subscribe sync time."):
                payload = iot_publish_SyncTime(self.mqttclient, self.productkey, self.devicename, 1, logger=self.logger)
                self.logger.info("message payload: {}".format(payload))
                # req_topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, "Time/Up")
                # rsp_topic = "/{0}/{1}/{2}".format(self.productkey, self.devicename, "Time/Down")
                # req_payload = {
                #     "action_id": "104",
                #     "data": "",
                #     "timestamp": str(get_timestamp())
                # }
                # self.logger.info("request topic: {0}".format(req_topic))
                # self.logger.info("request payload: {0}".format(req_payload))
                # self.logger.info("response topic: {0}".format(rsp_topic))
                # self.mqttclient.subscribe(rsp_topic, 1)
                # self.mqttclient.loopstart()
                # self.mqttclient.publish(req_topic, str(req_payload), 1)
                # start_time = int(time.time())
                # end_time = int(time.time())
                # during = end_time - start_time
                # while not self.mqttclient.rcv_msg and during < 60:
                #     sleep(5)
                #     end_time = int(time.time())
                #     during = end_time - start_time
                # self.mqttclient.loopstop()
                # self.mqttclient.unsubscribe(rsp_topic)
                # if self.mqttclient.rcv_msg:
                #     msg = self.mqttclient.rcv_msg.pop()
                #     payload = json.loads(msg.payload, encoding='utf-8')
                #     self.logger.info("message payload: {}".format(payload))
                # self.logger.info("MQTT receive sync time finished.")
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_xxx001_subscribe_create_service_order ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_iot.py'])
    pytest.main(['-s', 'test_iot.py::TestIOTSubscribe::test_xxx001_subscribe_create_service_order'])
