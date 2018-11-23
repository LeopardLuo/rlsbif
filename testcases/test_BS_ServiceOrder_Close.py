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


@allure.feature("业务系统-关闭服务单")
class TestCloseServiceOrder(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'BSCancelServiceOrder')
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
                        "imei": "460011234567890", "phone": "13511222281", "sms_code": "123456",
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

            with allure.step("teststep: user feature."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_myfeature(cls.httpclient, cls.member_id, 'face2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                cls.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep: identity user."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_identity(cls.httpclient, cls.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                cls.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep: identity relative."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result1 = identity_other(cls.httpclient, cls.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), cls.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                cls.logger.info("identity relative result: {0}".format(identity_result1))

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

            with allure.step("teststep: get features id by user info."):
                user_info = inner_auth(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
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
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.step("+++ setup method +++")
    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        with allure.step("teststep: create service orders"):
            order_result = inner_create_service_order(self.httpclient, self.system_id,
                                                      str(random.randint(1000, 100000)),
                                                      self.member_id, self.features_id, self.devices_ids, 3,
                                                      get_timestamp(), 9999999999, 10, random.randint(1000, 100000),
                                                      'testunit',
                                                      'dept1', get_timestamp(), self.logger)
            allure.attach("order list", str(order_result))
            self.logger.info("order list: {0}".format(order_result))
            self.service_order_id = order_result['service_order_id']
        with allure.step("teststep: check service order info"):
            order_info = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                  logger=self.logger)
            allure.attach("service order info：", str(order_info))
            self.logger.info("service order info: {}".format(order_info))
        self.logger.info("Add some datas to database.")
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        with allure.step("delete service order records"):
            table = 'bus_service_order_status'
            condition = ("service_order_id", self.service_order_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("")
            self.logger.info("table: {0}, condition: {1}".format(table, condition))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete service order records"):
            table = 'bus_service_order'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("")
            self.logger.info("table: {0}, condition: {1}".format(table, condition))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("do some database clean operation.")
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("撤销服务单成功")
    @allure.testcase("FT-HTJK-203-001")
    def test_203001_cancel_service_order_correct(self):
        """ Test cancel service order by correct parameters(FT-HTJK-203-001)."""
        self.logger.info(".... Start test_203001_cancel_service_order_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id, "system_code": self.system_code,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 5
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203001_cancel_service_order_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_id值")
    @allure.testcase("FT-HTJK-203-002")
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
                             ids=["system_id(超长值)", "system_id(0)", "system_id(最小值)", "system_id(最大值)", "system_id(-1)",
                                  "system_id(小数)",
                                  "system_id(超大)", "system_id(字母)", "system_id(中文)", "system_id(特殊字符)",
                                  "system_id(数字字母)",
                                  "system_id(数字中文)", "system_id(数字特殊字符)", "system_id(空格)", "system_id(空)"])
    def test_203002_system_id_wrong(self, system_id, result):
        """ Test wrong system_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-203-002).
        :param system_id: system_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203002_system_id_wrong ({}) ....".format(system_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203002_system_id_wrong ({}) ....".format(system_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误service_order_id值")
    @allure.testcase("FT-HTJK-203-003")
    @pytest.mark.parametrize("service_order_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101016, "msg": "service_order_id值非法"}),
                              (1, {"status": 200, "code": 101016, "msg": "service_order_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 101016, "msg": "服务单不存在"}),
                              (-1, {"status": 200, "code": 101016, "msg": "service_order_id值非法"}),
                              (1.5, {"status": 200, "code": 101016, "msg": "service_order_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["service_order_id(超长值)", "service_order_id(0)", "service_order_id(最小值)",
                                  "service_order_id(最大值)", "service_order_id(-1)", "service_order_id(小数)",
                                  "service_order_id(超大)", "service_order_id(字母)", "service_order_id(中文)",
                                  "service_order_id(特殊字符)", "service_order_id(数字字母)","service_order_id(数字中文)",
                                  "service_order_id(数字特殊字符)", "service_order_id(空格)", "service_order_id(空)"])
    def test_203003_service_order_id_wrong(self, service_order_id, result):
        """ Test wrong service_order_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-203-003).
        :param service_order_id: service_order_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203003_service_order_id_wrong ({}) ....".format(service_order_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": service_order_id,
                        "system_code": self.system_code,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203003_service_order_id_wrong ({}) ....".format(service_order_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_code值")
    @allure.testcase("FT-HTJK-203-004")
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
    def test_203004_system_code_wrong(self, system_code, result):
        """ Test wrong system_code values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-203-004).
        :param system_code: system_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203004_system_code_wrong ({}) ....".format(system_code))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": system_code, "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203004_system_code_wrong ({}) ....".format(system_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确close_code值")
    @allure.testcase("FT-HTJK-203-005")
    @pytest.mark.parametrize("close_code, result",
                             [(0, {"code": 1, "msg": 3}),
                              (1, {"code": 1, "msg": 5})],
                             ids=["close_code(0)", "close_code(1)"])
    def test_203005_close_code_correct(self, close_code, result):
        """ Test correct close_code values (0/1）(FT-HTJK-203-005).
        :param close_code: close_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203005_close_code_correct ({}) ....".format(close_code))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "close_code": close_code, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert not rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == result['msg']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203005_close_code_correct ({}) ....".format(close_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误close_code值")
    @allure.testcase("FT-HTJK-203-006")
    @pytest.mark.parametrize("close_code, result",
                             [(-1, {"status": 200, "code": 101017, "msg": "close_code值非法"}),
                              (2, {"status": 200, "code": 101017, "msg": "close_code值非法"}),
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
                              ('', {"status": 400, "code": 0, "msg": ""}) ],
                             ids=["close_code(-1)", "close_code(2)", "close_code(超小值)", "close_code(超大值)", "close_code(小数)",
                                  "close_code(字母)", "close_code(中文)", "close_code(特殊字符)", "close_code(数字字母)",
                                  "close_code(数字中文)", "close_code(数字特殊字符)", "close_code(空格)", "close_code(空)"])
    def test_203006_close_code_wrong(self, close_code, result):
        """ Test wrong close_code values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、
            数字特殊字符、空格、空）(FT-HTJK-203-006).
        :param close_code: close_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203006_close_code_wrong ({}) ....".format(close_code))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "close_code": close_code, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203006_close_code_wrong ({}) ....".format(close_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-203-007")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 100, {"code": 1, "msg": ""}),
                              (get_timestamp() + 100, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_203007_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-203-007).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203007_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "close_code": 1, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 5
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203007_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-203-008")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (9223372036854775807, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (0, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (-1, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (get_timestamp() - 1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (get_timestamp() + 1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
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
    def test_203008_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、允许超小值、允许超大值、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-203-008).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_203008_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "close_code": 1, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203008_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_id参数")
    @allure.testcase("FT-HTJK-203-009")
    def test_203009_no_system_id(self):
        """ Test close service order without system_id(FT-HTJK-203-009)."""
        self.logger.info(".... Start test_203009_no_system_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"service_order_id": self.service_order_id,
                        "system_code": self.system_code,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 101000
                assert 'system_id值非法' in rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id, self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203009_no_system_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少service_order_id参数")
    @allure.testcase("FT-HTJK-203-010")
    def test_203010_no_service_order_id(self):
        """ Test close service order without service_order_id(FT-HTJK-203-010)."""
        self.logger.info(".... Start test_203010_no_service_order_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id,
                        "system_code": self.system_code,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 101016
                assert 'service_order_id值非法' in rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203010_no_service_order_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_code参数")
    @allure.testcase("FT-HTJK-203-011")
    def test_203011_no_system_code(self):
        """ Test close service order without system_code(FT-HTJK-203-011)."""
        self.logger.info(".... Start test_203011_no_system_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id,
                        "service_order_id": self.service_order_id,
                        "close_code": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 202005
                assert '授权非法' in rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203011_no_system_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少close_code参数")
    @allure.testcase("FT-HTJK-203-012")
    def test_203012_no_close_code(self):
        """ Test close service order without close_code(FT-HTJK-203-012)."""
        self.logger.info(".... Start test_203012_no_close_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 202005
                assert '' in rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203012_no_close_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-203-013")
    def test_203013_no_timestamp(self):
        """ Test close service order without timestamp(FT-HTJK-203-013)."""
        self.logger.info(".... Start test_203013_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"system_id": self.system_id, "service_order_id": self.service_order_id,
                        "system_code": self.system_code, "close_code": 1}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 101002
                assert 'timestamp值非法' in rsp_content["message"]

            with allure.step("teststep5: check service order info"):
                order_info = bs_get_service_order_status(self.httpclient, self.system_id, self.service_order_id,
                                                         self.system_code, get_timestamp(), self.logger)
                allure.attach("service order info：", str(order_info))
                self.logger.info("service order info: {}".format(order_info))
                assert order_info['state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_203013_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_BS_ServiceOrder_Close.py'])
    pytest.main(['-s', 'test_BS_ServiceOrder_Close.py::TestCloseServiceOrder::test_203001_cancel_service_order_correct'])
