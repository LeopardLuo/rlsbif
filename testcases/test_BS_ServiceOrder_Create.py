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


@allure.feature("创建服务单")
class TestCreateServiceOrder(object):

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
                        "imei": "460011234567890", "phone": "13511222241", "sms_code": "123456",
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
    @allure.testcase("FT-HTJK-201-001")
    def test_201001_create_service_order_correct(self):
        """ Test create service order with correct parameters(FT-HTJK-201-001)."""
        self.logger.info(".... Start test_201001_create_service_order_correct ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),"member_id": self.member_id,
                        "system_code": self.system_code, "features_id": self.features_id, "device_ids": self.devices_ids,
                        "verify_condition_type": 2, "begin_time": get_timestamp(), "end_time": 9999999999,
                        "in_count": 1, "service_unit": 'unit1', "service_address": 'dept1', "timestamp": get_timestamp()}
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
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(".... End test_201001_create_service_order_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_id值")
    @allure.testcase("FT-HTJK-201-002")
    @pytest.mark.parametrize("system_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (1, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 202004, "msg": "该业务系统不存在"}),
                              (-1, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (1.0, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["system_id(超长值)", "system_id(0)", "system_id(最小值)", "system_id(最大值)", "system_id(-1)", "system_id(小数)",
                                  "system_id(超大)", "system_id(字母)", "system_id(中文)", "system_id(特殊字符)", "system_id(数字字母)",
                                  "system_id(数字中文)", "system_id(数字特殊字符)", "system_id(空格)", "system_id(空)"])
    def test_201002_system_id_wrong(self, system_id, result):
        """ Test wrong system_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-002).
        :param system_id: system_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201002_system_id_wrong ({}) ....".format(system_id))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
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
                print(rsp.json())
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201002_system_id_wrong ({}) ....".format(system_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确business_order_id值")
    @allure.testcase("FT-HTJK-201-003")
    @pytest.mark.parametrize("business_order_id, result",
                             [(1.0, {"code": 1, "msg": ""}),
                              ('a', {"code": 1, "msg": ""}),
                              ('中文', {"code": 1, "msg": ""}),
                              ('**', {"code": 1, "msg": ""}),
                              ('1a', {"code": 1, "msg": ""}),
                              ('1中文', {"code": 1, "msg": ""}),
                              ('1**', {"code": 1, "msg": ""})],
                             ids=["business_order_id(小数)", "business_order_id(字母)", "business_order_id(中文)",
                                  "business_order_id(特殊字符)", "business_order_id(数字字母)", "business_order_id(数字中文)",
                                  "business_order_id(数字特殊字符)"])
    def test_201003_business_order_id_correct(self, business_order_id, result):
        """ Test correct business_order_id values (1.0、超大值、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符）(FT-HTJK-201-003).
        :param business_order_id: business_order_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201003_business_order_id_wrong ({}) ....".format(business_order_id))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": business_order_id,
                         "member_id": self.member_id,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(".... End test_201003_business_order_id_wrong ({}) ....".format(business_order_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误business_order_id值")
    @allure.testcase("FT-HTJK-201-004")
    @pytest.mark.parametrize("business_order_id, result",
                             [('1'*1001, {"code": 202999, "msg": "下单失败,请重试"}),
                              (' ', {"code": 101009, "msg": "business_order_id值非法"}),
                              ('', {"code": 101009, "msg": "business_order_id值非法"})],
                             ids=["business_order_id(超长值)", "business_order_id(空格)", "business_order_id(空)"])
    def test_201004_business_order_id_wrong(self, business_order_id, result):
        """ Test wrong business_order_id values (超长值、空格、空）(FT-HTJK-201-004).
        :param business_order_id: business_order_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201004_business_order_id_wrong ({}) ....".format(business_order_id))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": business_order_id,
                         "member_id": self.member_id,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201004_business_order_id_wrong ({}) ....".format(business_order_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-201-005")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (1, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 202007, "msg": "客户特征不存在"}),
                              (-1, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (1.0, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(0)", "member_id(最小值)", "member_id(最大值)", "member_id(-1)",
                                  "member_id(小数)",
                                  "member_id(超大)", "member_id(字母)", "member_id(中文)", "member_id(特殊字符)",
                                  "member_id(数字字母)",
                                  "member_id(数字中文)", "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_201005_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-005).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201005_member_id_wrong ({}) ....".format(member_id))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": member_id,
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201005_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_code值")
    @allure.testcase("FT-HTJK-201-006")
    @pytest.mark.parametrize("system_code, result",
                             [('1' * 1001, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (0, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (1, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (-1, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (1.0, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('a', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('中', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('*', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1a', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1中', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1*', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (' ', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('', {"status": 200, "code": 202005, "msg": "授权非法"})],
                             ids=["system_code(超长值)", "system_code(0)", "system_code(最小值)", "system_code(-1)",
                                  "system_code(小数)", "system_code(字母)", "system_code(中文)", "system_code(特殊字符)",
                                  "system_code(数字字母)",
                                  "system_code(数字中文)", "system_code(数字特殊字符)", "system_code(空格)", "system_code(空)"])
    def test_201006_system_code_wrong(self, system_code, result):
        """ Test wrong system_code values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-006).
        :param system_code: system_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201006_system_code_wrong ({}) ....".format(system_code))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": system_code, "features_id": self.features_id,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201006_system_code_wrong ({}) ....".format(system_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误features_id值")
    @allure.testcase("FT-HTJK-201-007")
    @pytest.mark.parametrize("features_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101007, "msg": "features_id值非法"}),
                              (1, {"status": 200, "code": 101007, "msg": "features_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 202007, "msg": "客户特征不存在"}),
                              (-1, {"status": 200, "code": 101007, "msg": "features_id值非法"}),
                              (1.0, {"status": 200, "code": 101007, "msg": "features_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 202005, "msg": "授权非法"}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["features_id(超长值)", "features_id(0)", "features_id(最小值)", "features_id(最大值)", "features_id(-1)",
                                  "features_id(小数)",
                                  "features_id(超大)", "features_id(字母)", "features_id(中文)", "features_id(特殊字符)",
                                  "features_id(数字字母)",
                                  "features_id(数字中文)", "features_id(数字特殊字符)", "features_id(空格)", "features_id(空)"])
    def test_201007_features_id_wrong(self, features_id, result):
        """ Test wrong member_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-007).
        :param features_id: features_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201007_features_id_wrong ({}) ....".format(features_id))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": features_id,
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201007_features_id_wrong ({}) ....".format(features_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确device_ids值")
    @allure.testcase("FT-HTJK-201-008")
    @pytest.mark.parametrize("device_ids, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2, {"status": 200, "code": 1, "msg": ""})],
                             ids=["device_ids(超长值)", "device_ids(0)"])
    def test_201008_device_ids_correct(self, device_ids, result):
        """ Test correct device_ids values (最小值、最大值）(FT-HTJK-201-008).
        :param device_ids: device_ids parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201008_device_ids_correct ({}) ....".format(device_ids))
        service_order_id = None
        if device_ids == 1:
            device_ids = [self.devices_ids[0]]
        else:
            device_ids = self.devices_ids
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": device_ids,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(".... End test_201008_device_ids_correct ({}) ....".format(device_ids))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误device_ids值")
    @allure.testcase("FT-HTJK-201-009")
    @pytest.mark.parametrize("device_ids, result",
                             [(['1' * 1001], {"status": 400, "code": 0, "msg": ""}),
                              ([0], {"status": 200, "code": 202009, "msg": "不合法"}),
                              ([1], {"status": 200, "code": 202009, "msg": "不合法"}),
                              ([9223372036854775807], {"status": 200, "code": 202009, "msg": "不合法"}),
                              ([-1], {"status": 200, "code": 202009, "msg": "不合法"}),
                              ([1.0], {"status": 200, "code": 202009, "msg": "不合法"}),
                              ([9223372036854775808], {"status": 400, "code": 0, "msg": ""}),
                              (['a'], {"status": 400, "code": 0, "msg": ""}),
                              (['中'], {"status": 400, "code": 0, "msg": ""}),
                              (['*'], {"status": 400, "code": 0, "msg": ""}),
                              (['1a'], {"status": 400, "code": 0, "msg": ""}),
                              (['1中'], {"status": 400, "code": 0, "msg": ""}),
                              (['1*'], {"status": 400, "code": 0, "msg": ""}),
                              ([' '], {"status": 400, "code": 0, "msg": ""}),
                              ([], {"status": 200, "code": 101015, "msg": "非法"}),
                              (23986546000789504, {"status": 400, "code": 0, "msg": ""})],
                             ids=["device_ids(超长值)", "device_ids(0)", "device_ids(最小值)", "device_ids(最大值)",
                                  "device_ids(-1)",  "device_ids(小数)",
                                  "device_ids(超大)", "device_ids(字母)", "device_ids(中文)", "device_ids(特殊字符)",
                                  "device_ids(数字字母)",
                                  "device_ids(数字中文)", "device_ids(数字特殊字符)", "device_ids(空格)", "device_ids(空)", "device_ids(非数组)"])
    def test_201009_device_ids_wrong(self, device_ids, result):
        """ Test wrong device_ids values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-009).
        :param device_ids: device_ids parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201009_device_ids_wrong ({}) ....".format(device_ids))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": device_ids,
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201009_device_ids_wrong ({}) ....".format(device_ids))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确verify_condition_type值")
    @allure.testcase("FT-HTJK-201-010")
    @pytest.mark.parametrize("verify_condition_type, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2, {"status": 200, "code": 1, "msg": ""}),
                              (3, {"status": 200, "code": 1, "msg": ""})],
                             ids=["verify_condition_type(1)", "verify_condition_type(2)", "verify_condition_type(3)"])
    def test_201010_verify_condition_type_correct(self, verify_condition_type, result):
        """ Test correct verify_condition_type values (1/2/3）(FT-HTJK-201-010).
        :param verify_condition_type: verify_condition_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201010_verify_condition_type_correct ({}) ....".format(verify_condition_type))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": verify_condition_type, "begin_time": get_timestamp(), "end_time": 9999999999,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(".... End test_201010_verify_condition_type_correct ({}) ....".format(verify_condition_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误verify_condition_type值")
    @allure.testcase("FT-HTJK-201-011")
    @pytest.mark.parametrize("verify_condition_type, result",
                             [(-1, {"status": 200, "code": 101012, "msg": "verify_condition_type值非法"}),
                              (0, {"status": 200, "code": 101012, "msg": "verify_condition_type值非法"}),
                              (4, {"status": 200, "code": 101012, "msg": "verify_condition_type值非法"}),
                              (-2147483649, {"status": 400, "code": 0, "msg": ""}),
                              (2147483648, {"status": 400, "code": 0, "msg": ""}),
                              (1.5, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}), ],
                             ids=["verify_condition_type(-1)", "verify_condition_type(0)", "verify_condition_type(5)",
                                  "verify_condition_type(超小值)", "verify_condition_type(超大值)", "code_type(小数)",
                                  "verify_condition_type(字母)", "verify_condition_type(中文)", "verify_condition_type(特殊字符)",
                                  "verify_condition_type(数字字母)", "verify_condition_type(数字中文)",
                                  "verify_condition_type(数字特殊字符)", "verify_condition_type(空格)", "verify_condition_type(空)"])
    def test_201011_verify_condition_type_wrong(self, verify_condition_type, result):
        """ Test wrong verify_condition_type values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、
            数字特殊字符、空格、空）(FT-HTJK-201-011).
        :param verify_condition_type: verify_condition_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201011_verify_condition_type_wrong ({}) ....".format(verify_condition_type))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": verify_condition_type, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201011_verify_condition_type_wrong ({}) ....".format(verify_condition_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确begin_time值")
    @allure.testcase("FT-HTJK-201-012")
    @pytest.mark.parametrize("begin_time, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (9999999998, {"status": 200, "code": 1, "msg": ""})],
                             ids=["begin_time(最小值)", "begin_time(最大值)"])
    def test_201012_begin_time_correct(self, begin_time, result):
        """ Test correct begin_time values (最小值、最大值）(FT-HTJK-201-012).
        :param begin_time: begin_time parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201012_begin_time_correct ({}) ....".format(begin_time))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": begin_time,
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'unit1', "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201012_begin_time_correct ({}) ....".format(begin_time))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误begin_time值")
    @allure.testcase("FT-HTJK-201-013")
    @pytest.mark.parametrize("begin_time, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101004, "msg": "begin_time值非法"}),
                              (10000000000, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (-1, {"status": 200, "code": 101004, "msg": "begin_time值非法"}),
                              (1.5, {"status": 200, "code": 101004, "msg": "begin_time值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                                (8888888888, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"})],
                             ids=["begin_time(超长值)", "begin_time(0)", "begin_time(最大值)",
                                  "begin_time(-1)",  "begin_time(小数)", "begin_time(超大)", "begin_time(字母)",
                                  "begin_time(中文)", "begin_time(特殊字符)", "begin_time(数字字母)",
                                  "begin_time(数字中文)", "begin_time(数字特殊字符)", "begin_time(空格)", "begin_time(空)", "begin_time(比end大)"])
    def test_201013_begin_time_wrong(self, begin_time, result):
        """ Test wrong begin_time values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-201-013).
        :param begin_time: begin_time parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201013_begin_time_wrong ({}) ....".format(begin_time))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": begin_time,
                         "end_time": 5555555555,
                         "in_count": 10, "service_unit": 'unit1', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201013_begin_time_wrong ({}) ....".format(begin_time))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确end_time值")
    @allure.testcase("FT-HTJK-201-014")
    @pytest.mark.parametrize("end_time, result",
                             [(2, {"status": 200, "code": 1, "msg": ""}),
                              (9999999999, {"status": 200, "code": 1, "msg": ""})],
                             ids=["end_time(最小值)", "end_time(最大值)"])
    def test_201014_end_time_correct(self, end_time, result):
        """ Test correct end_time values (最小值、最大值）(FT-HTJK-201-014).
        :param end_time: end_time parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201014_end_time_correct ({}) ....".format(end_time))
        service_order_id = None
        end_time = get_timestamp() if end_time == 2 else end_time
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": 1,
                         "end_time": end_time,
                         "in_count": 10, "service_unit": 'unit1', "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201014_end_time_correct ({}) ....".format(end_time))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误end_time值")
    @allure.testcase("FT-HTJK-201-015")
    @pytest.mark.parametrize("end_time, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (10000000000, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (-1, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (1.5, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (1000000000, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"})],
                             ids=["end_time(超长值)", "end_time(0)", "end_time(最大值)",
                                  "end_time(-1)", "end_time(小数)", "end_time(超大)", "end_time(字母)",
                                  "end_time(中文)", "end_time(特殊字符)", "end_time(数字字母)",
                                  "end_time(数字中文)", "end_time(数字特殊字符)", "end_time(空格)", "end_time(空)",
                                  "end_time(过期)"])
    def test_201015_end_time_wrong(self, end_time, result):
        """ Test wrong end_time values (超长值、0、允许超大值、-1、1.5、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空、过期值）(FT-HTJK-201-015).
        :param end_time: end_time parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201015_end_time_wrong ({}) ....".format(end_time))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": end_time,
                         "in_count": 10, "service_unit": 'unit1', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201015_end_time_wrong ({}) ....".format(end_time))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("检查次数时间空")
    @allure.testcase("FT-HTJK-201-016")
    @pytest.mark.parametrize("check_time, result",
                             [(' ', {"status": 200, "code": 1, "msg": ""}),
                              ('', {"status": 200, "code": 1, "msg": ""})],
                             ids=["check_time(空格)", "check_time(空)"])
    def test_201016_check_time_empty(self, check_time, result):
        """ Test check_time values (空格、空）(FT-HTJK-201-016).
        :param check_time: check_time parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201016_check_time_empty ({}) ....".format(check_time))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 2, "begin_time": check_time,
                         "end_time": check_time,
                         "in_count": 10, "service_unit": 'unit1', "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201016_check_time_empty ({}) ....".format(check_time))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确in_count值")
    @allure.testcase("FT-HTJK-201-017")
    @pytest.mark.parametrize("in_count, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2147483647, {"status": 200, "code": 1, "msg": ""})],
                             ids=["in_count(最小值)", "in_count(最大值)"])
    def test_201017_in_count_correct(self, in_count, result):
        """ Test in_count values (最小值、最大值）(FT-HTJK-201-017).
        :param in_count: in_count parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201017_in_count_correct ({}) ....".format(in_count))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 2, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": in_count, "service_unit": 'unit1', "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201017_in_count_correct ({}) ....".format(in_count))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误in_count值")
    @allure.testcase("FT-HTJK-201-018")
    @pytest.mark.parametrize("in_count, result",
                             [(-1, {"status": 200, "code": 101011, "msg": "in_count值非法"}),
                              (0, {"status": 200, "code": 101011, "msg": "in_count值非法"}),
                              (-2147483649, {"status": 400, "code": 0, "msg": ""}),
                              (2147483648, {"status": 400, "code": 0, "msg": ""}),
                              (1.5, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}), ],
                             ids=["in_count(-1)", "in_count(0)",
                                  "in_count(超小值)", "in_count(超大值)", "in_count(小数)",
                                  "in_count(字母)", "in_count(中文)", "in_count(特殊字符)",
                                  "in_count(数字字母)", "in_count(数字中文)",
                                  "in_count(数字特殊字符)", "in_count(空格)", "in_count(空)"])
    def test_201018_in_count_wrong(self, in_count, result):
        """ Test wrong in_count values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、
            数字特殊字符、空格、空）(FT-HTJK-201-018).
        :param in_count: in_count parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201018_in_count_wrong ({}) ....".format(in_count))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 2, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": in_count, "service_unit": 'unit1', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201018_in_count_wrong ({}) ....".format(in_count))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("检查时间次数空")
    @allure.testcase("FT-HTJK-201-019")
    @pytest.mark.parametrize("in_count, result",
                             [(' ', {"status": 200, "code": 1, "msg": ""}),
                              ('', {"status": 200, "code": 1, "msg": ""})],
                             ids=["in_count(空格)", "in_count(空)"])
    def test_201019_in_count_empty(self, in_count, result):
        """ Test in_count values (空格、空）(FT-HTJK-201-019).
        :param in_count: in_count parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201019_in_count_empty ({}) ....".format(in_count))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 1, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": in_count, "service_unit": 'unit1', "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201019_in_count_empty ({}) ....".format(in_count))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确service_unit值")
    @allure.testcase("FT-HTJK-201-020")
    @pytest.mark.parametrize("service_unit, result",
                             [('1' * 100, {"code": 1, "msg": ""}),
                              ('1.0', {"code": 1, "msg": ""}),
                              ('abc', {"code": 1, "msg": ""}),
                              ('中', {"code": 1, "msg": ""}),
                              ('*', {"code": 1, "msg": ""}),
                              ('1a中', {"code": 1, "msg": ""}),
                              ('1a*', {"code": 1, "msg": ""})],
                             ids=["service_unit(最大长度值)", "service_unit(小数)", "service_unit(字母)", "service_unit(中文)",
                                  "service_unit(特殊字符)", "service_unit(数字字母中文)", "service_unit(数字字母特殊字符)"])
    def test_201020_service_unit_correct(self, service_unit, result):
        """ Test correct service_unit values (最大长度值、1.0、字母、中文、特殊字符、数字字母中文、数字字母特殊字符）(FT-HTJK-201-020).
        :param service_unit: service_unit parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201020_service_unit_correct ({}) ....".format(service_unit))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": service_unit, "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201020_service_unit_correct ({}) ....".format(service_unit))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误service_unit值")
    @allure.testcase("FT-HTJK-201-021")
    @pytest.mark.parametrize("service_unit, result",
                             [('1' * 256, {"code": 202999, "msg": "下单失败"}),
                              (' ', {"code": 101013, "msg": "service_unit值非法"}),
                              ('', {"code": 101013, "msg": "service_unit值非法"})],
                             ids=["service_unit(超长值)", "service_unit(空格)", "service_unit(空)"])
    def test_201021_service_unit_wrong(self, service_unit, result):
        """ Test wrong service_unit values (超长值、空格、空）(FT-HTJK-201-021).
        :param service_unit: service_unit parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201021_service_unit_wrong ({}) ....".format(service_unit))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": service_unit, "service_address": 'dept1',
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201021_service_unit_wrong ({}) ....".format(service_unit))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确service_address值")
    @allure.testcase("FT-HTJK-201-022")
    @pytest.mark.parametrize("service_address, result",
                             [('1' * 100, {"code": 1, "msg": ""}),
                              (1.5, {"code": 1, "msg": ""}),
                              ('abc', {"code": 1, "msg": ""}),
                              ('中', {"code": 1, "msg": ""}),
                              ('*', {"code": 1, "msg": ""}),
                              ('1a中', {"code": 1, "msg": ""}),
                              ('1a*', {"code": 1, "msg": ""})],
                             ids=["service_address(最大长度值)", "service_address(小数)", "service_address(字母)", "service_address(中文)",
                                  "service_address(特殊字符)", "service_address(数字字母中文)", "service_address(数字字母特殊字符)"])
    def test_201022_service_address_correct(self, service_address, result):
        """ Test correct service_address values (最大长度值、1.0、字母、中文、特殊字符、数字字母中文、数字字母特殊字符）(FT-HTJK-201-022).
        :param service_address: service_address parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201022_service_address_correct ({}) ....".format(service_address))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'test', "service_address": service_address,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201022_service_address_correct ({}) ....".format(service_address))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误service_address值")
    @allure.testcase("FT-HTJK-201-023")
    @pytest.mark.parametrize("service_address, result",
                             [('1' * 256, {"code": 202999, "msg": "下单失败"}),
                              (' ', {"code": 101014, "msg": "service_address值非法"}),
                              ('', {"code": 101014, "msg": "service_address值非法"})],
                             ids=["service_address(超长值)", "service_address(空格)", "service_address(空)"])
    def test_201023_service_address_wrong(self, service_address, result):
        """ Test wrong service_address values (超长值、空格、空）(FT-HTJK-201-023).
        :param service_address: service_address parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201023_service_address_wrong ({}) ....".format(service_address))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'test', "service_address": service_address,
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201023_service_address_wrong ({}) ....".format(service_address))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-201-024")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 100, {"code": 1, "msg": ""}),
                              (get_timestamp() + 100, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_201024_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-201-024).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201024_timestamp_correct ({}) ....".format(timestamp))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'test', "service_address": 'dept1',
                         "timestamp": timestamp}
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
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(
                ".... End test_201024_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-201-025")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (9223372036854775807, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (0, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (-1, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (get_timestamp()-1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (get_timestamp()+1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (1.5, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              ('a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              (' ', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('', {"status": 400, "code": 0, "msg": "is invalid"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(允许超小值)", "timestamp(允许超大值)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_201025_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、允许超小值、允许超大值、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-201-025).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201025_timestamp_wrong ({}) ....".format(timestamp))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(),
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'test', "service_address": 'dept1',
                         "timestamp": timestamp}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(
                ".... End test_201025_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_id参数")
    @allure.testcase("FT-HTJK-201-026")
    def test_201026_no_system_id(self):
        """ Test create service order without system_id(FT-HTJK-201-026)."""
        self.logger.info(".... Start test_201026_no_system_id ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
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
                assert rsp_content["code"] == 101000
                assert 'system_id值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201026_no_system_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少business_order_id参数")
    @allure.testcase("FT-HTJK-201-027")
    def test_201027_no_business_order_id(self):
        """ Test create service order without business_order_id(FT-HTJK-201-027)."""
        self.logger.info(".... Start test_201027_no_business_order_id ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "member_id": self.member_id,
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
                assert rsp_content["code"] == 101009
                assert 'business_order_id值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201027_no_business_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-201-028")
    def test_201028_no_member_id(self):
        """ Test create service order without member_id(FT-HTJK-201-028)."""
        self.logger.info(".... Start test_201028_no_member_id ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
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
                assert rsp_content["code"] == 101001
                assert 'member_id值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201028_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_code参数")
    @allure.testcase("FT-HTJK-201-029")
    def test_201029_no_system_code(self):
        """ Test create service order without system_code(FT-HTJK-201-029)."""
        self.logger.info(".... Start test_201029_no_system_code ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "features_id": self.features_id,
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
                assert rsp_content["code"] == 202005
                assert '授权非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201029_no_system_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少features_id参数")
    @allure.testcase("FT-HTJK-201-030")
    def test_201030_no_features_id(self):
        """ Test create service order without features_id(FT-HTJK-201-030)."""
        self.logger.info(".... Start test_201030_no_features_id ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
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
                assert rsp_content["code"] == 101007
                assert 'features_id值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201030_no_features_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_ids参数")
    @allure.testcase("FT-HTJK-201-031")
    def test_201031_no_device_ids(self):
        """ Test create service order without device_ids(FT-HTJK-201-031)."""
        self.logger.info(".... Start test_201031_no_device_ids ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
                         "features_id": self.features_id,
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
                assert rsp_content["code"] == 101015
                assert 'device_ids值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201031_no_device_ids ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少verify_condition_type参数")
    @allure.testcase("FT-HTJK-201-032")
    def test_201032_no_verify_condition_type(self):
        """ Test create service order without verify_condition_type(FT-HTJK-201-032)."""
        self.logger.info(".... Start test_201032_no_verify_condition_type ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
                         "features_id": self.features_id,
                         "device_ids": self.devices_ids, "begin_time": get_timestamp(), "end_time": 9999999999,
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
                assert rsp_content["code"] == 101012
                assert 'verify_condition_type值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201032_no_verify_condition_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少begin_time参数")
    @allure.testcase("FT-HTJK-201-033")
    @pytest.mark.parametrize("condition_type, result",
                             [(1, {"status": 200, "code": 101011, "msg": "in_count值非法"}),
                              (2, {"status": 200, "code": 1, "msg": ""}),
                              (3, {"status": 200, "code": 101011, "msg": "in_count值非法"})],
                             ids=["condition_type(最大长度值)", "condition_type(小数)", "condition_type(字母)"])
    def test_201033_no_begin_time(self, condition_type, result):
        """ Test create service order without begin time with condition type (1/2/3）(FT-HTJK-201-033).
        :param condition_type: condition_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201033_no_begin_time ({}) ....".format(condition_type))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": condition_type,
                         "end_time": 9999999999,
                         "in_count": 10, "service_unit": 'test', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
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
            self.logger.info(
                ".... End test_201033_no_begin_time ({}) ....".format(condition_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少end_time参数")
    @allure.testcase("FT-HTJK-201-034")
    @pytest.mark.parametrize("condition_type, result",
                             [(1, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"}),
                              (2, {"status": 200, "code": 1, "msg": ""}),
                              (3, {"status": 200, "code": 101006, "msg": "结束时间必须晚于开始时间"})],
                             ids=["condition_type(最大长度值)", "condition_type(小数)", "condition_type(字母)"])
    def test_201034_no_end_time(self, condition_type, result):
        """ Test create service order without end time with condition type (1/2/3）(FT-HTJK-201-034).
        :param condition_type: condition_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201034_no_end_time ({}) ....".format(condition_type))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": condition_type,
                         "begin_time": get_timestamp(),
                         "in_count": 10, "service_unit": 'test', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
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
            self.logger.info(
                ".... End test_201034_no_end_time ({}) ....".format(condition_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少in_count参数")
    @allure.testcase("FT-HTJK-201-035")
    @pytest.mark.parametrize("condition_type, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2, {"status": 200, "code": 101011, "msg": "in_count值非法"}),
                              (3, {"status": 200, "code": 101011, "msg": "in_count值非法"})],
                             ids=["condition_type(最大长度值)", "condition_type(小数)", "condition_type(字母)"])
    def test_201035_no_in_count(self, condition_type, result):
        """ Test create service order without in_count with condition type (1/2/3）(FT-HTJK-201-035).
        :param condition_type: condition_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_201035_no_in_count ({}) ....".format(condition_type))
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": self.features_id,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": condition_type,
                         "begin_time": get_timestamp(),
                         "end_time": 9999999999, "service_unit": 'test', "service_address": 'dept1',
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        service_order_id = rsp_content['result']['service_order_id']
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
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
            self.logger.info(
                ".... End test_201035_no_in_count ({}) ....".format(condition_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少service_unit参数")
    @allure.testcase("FT-HTJK-201-036")
    def test_201036_no_service_unit(self):
        """ Test create service order without service_unit(FT-HTJK-201-036)."""
        self.logger.info(".... Start test_201036_no_service_unit ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
                         "features_id": self.features_id, "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(), "end_time": 9999999999,
                         "in_count": 1, "service_address": 'dept1',
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
                assert rsp_content["code"] == 101013
                assert 'service_unit值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201036_no_service_unit ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少service_address参数")
    @allure.testcase("FT-HTJK-201-037")
    def test_201037_no_service_address(self):
        """ Test create service order without service_address(FT-HTJK-201-037)."""
        self.logger.info(".... Start test_201037_no_service_address ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
                         "features_id": self.features_id, "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(), "end_time": 9999999999,
                         "in_count": 1, "service_unit": 'test',
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
                assert rsp_content["code"] == 101014
                assert 'service_address值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201037_no_service_address ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-201-038")
    def test_201038_no_timestamp(self):
        """ Test create service order without timestamp(FT-HTJK-201-038)."""
        self.logger.info(".... Start test_201038_no_timestamp ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get parameters."):
                datas = {"system_id": self.system_id,
                         "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id, "system_code": self.system_code,
                         "features_id": self.features_id, "device_ids": self.devices_ids,
                         "verify_condition_type": 3, "begin_time": get_timestamp(), "end_time": 9999999999,
                         "in_count": 1, "service_unit": 'test',
                         "service_address": 'dept1'}
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
                assert rsp_content["code"] == 101002
                assert 'timestamp值非法' in rsp_content['message']

            with allure.step("teststep6: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 0
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
            self.logger.info(".... End test_201038_no_timestamp ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("创建本人服务单成功")
    @allure.testcase("FT-HTJK-201-001")
    def test_201001_create_service_order_owner(self):
        """ Test create service order of owner(FT-HTJK-201-001)."""
        self.logger.info(".... Start test_201001_create_service_order_owner ....")
        service_order_id = None
        try:
            with allure.step("teststep1: get business token."):
                self.httpclient.update_header({"authorization": self.token})
                business_result = h5_get_business_token(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("business token", str(business_result))
                self.logger.info("business token: {}".format(business_result))
                business_token = business_result['business_token']

            with allure.step("teststep2: get user features id."):
                user_info = bs_get_user_info(self.httpclient, self.system_id, self.member_id, business_token, get_timestamp(), self.logger)
                allure.attach("user_info", str(user_info))
                self.logger.info("user_info: {}".format(user_info))
                for item in user_info['features_info']:
                    if item['features_name'] == '本人':
                        user_features = item['features_id']
                        break
                self.logger.info("user_features: {}".format(user_features))
                assert user_features

            with allure.step("teststep3: get parameters."):
                datas = {"system_id": self.system_id, "business_order_id": str(random.randint(100000, 1000000)),
                         "member_id": self.member_id,
                         "system_code": self.system_code, "features_id": user_features,
                         "device_ids": self.devices_ids,
                         "verify_condition_type": 2, "begin_time": get_timestamp(), "end_time": 9999999999,
                         "in_count": 1, "service_unit": 'unit1', "service_address": 'dept1',
                         "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(datas))
                self.logger.info("data: {0}".format(datas))

            with allure.step("teststep4: requests http post."):
                self.httpclient.update_header({"authorization": None})
                rsp = self.httpclient.post(self.URI, json=datas)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep5: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep6: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp_content["code"] == 1:
                    service_order_id = rsp_content['result']['service_order_id']
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']

            with allure.step("teststep7: get service order list"):
                self.httpclient.update_header({"authorization": self.token})
                order_list = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3,
                                                      timestamp=get_timestamp(), logger=self.logger)
                self.httpclient.update_header({"authorization": None})
                self.logger.info("")
                self.logger.info("service order list: {0}".format(order_list))
                allure.attach("service order list", str(order_list))
                assert len(order_list) == 1
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
            self.logger.info(".... End test_201001_create_service_order_owner ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_BS_ServiceOrder_Create.py'])
    # pytest.main(['-s', 'test_BS_ServiceOrder_Create.py::TestCreateServiceOrder::test_201001_create_service_order_owner'])
