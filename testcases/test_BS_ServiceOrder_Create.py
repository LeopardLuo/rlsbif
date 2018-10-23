#!/usr/bin/env python3
# -*-coding:utf-8-*-

import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *


@allure.feature("业务系统创建服务单")
class TestBSCreateServiceOrder(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'BSCreateServiceOrder')
                allure.attach("uri", str(cls.URI))
                cls.logger.info("uri: " + cls.URI)
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
                        "imei": "460011234567890", "phone": "13511222341", "sms_code": "123456",
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

            with allure.step("teststep: get features id."):
                feature_data = get_identity_other_list(cls.httpclient, cls.member_id, 0, 10, get_timestamp(), logger=cls.logger)
                allure.attach("features data list", "{0}".format(feature_data))
                cls.logger.info("features data list: {0}".format(feature_data))
                cls.features_id = feature_data[0]['features_id']

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
                table = 'bus_device'
                condition = ("system_id", cls.system_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.devices_ids = []
                for device in select_result:
                    cls.devices_ids.append(device[0])
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
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("blocker")
    @allure.story("创建关联人服务单成功")
    @allure.testcase("FT-HTJK-207-001")
    def test_207001_create_service_order_correct(self):
        """ Test create service order with correct parameters(FT-HTJK-207-001)."""
        self.logger.info(".... Start test_207001_create_service_order_correct ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 2, "begin_time": get_timestamp(), "end_time": 9999999999,
                         "in_count": 1, "service_unit": 'unit1', "service_address": 'dept1',
                         "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(datas))
                self.logger.info("data: {0}".format(datas))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header({"authorization": None})
                rsp = self.httpclient.post(self.URI, json=datas)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp_content["code"] == 1:
                    service_order_id = rsp_content['result']['service_order_id']
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']

            with allure.step("teststep6: get service order list"):
                order_status = bs_get_service_order_status(self.httpclient, self.system_id, service_order_id, self.system_code, get_timestamp(), self.logger)
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_status))
                allure.attach("service order list", str(order_status))

        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            if service_order_id:
                with allure.step("delete service order records"):
                    table = 'bus_service_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    delete_result = self.mysql.execute_delete_condition(table, condition)
                    allure.attach("delete result", str(delete_result))
                    self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_207001_create_service_order_correct ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_BS_ServiceOrder_Create.py'])
    pytest.main(['-s', 'test_BS_ServiceOrder_Create.py::TestBSCreateServiceOrder::test_207001_create_service_order_correct'])
