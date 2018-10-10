#!/usr/bin/env python3
# -*-coding:utf-8-*-

import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *


@allure.feature("注册-完成注册")
class TestRegister(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'Register')
                allure.attach("uri", cls.URI)
                cls.logger.info("uri: " + cls.URI)
            with allure.step("初始化HTTP客户端。"):
                sv_protocol = cls.config.getItem('server', 'protocol')
                sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, sv_port)
                allure.attach("baseurl", baseurl)
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)
            with allure.step("初始化数据库连接。"):
                db_user = cls.config.getItem('db', 'db_user')
                db_password = cls.config.getItem('db', 'db_password')
                db_host = cls.config.getItem('db', 'db_host')
                db_database = cls.config.getItem('db', 'db_database')
                db_port = int(cls.config.getItem('db', 'db_port'))
                allure.attach("db_params", (db_user, db_password, db_host, db_database, db_port))
                cls.logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)
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
        with allure.step("Clear user register table info"):
            table = 'member'
            condition = ('user', '1351122%')
            allure.attach("table and condition", (table, condition))
            self.logger.info("table: {0}, condition: {1}".format(table, condition))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", delete_result)
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("Add some datas to database.")
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("do some database clean operation.")
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("注册成功")
    @allure.testcase("FT-HTJK-102-001")
    def test_102001_register_correct(self):
        """ Test register by correct parameters(FT-HTJK-102-001)."""
        self.logger.info(".... Start test_102001_register_correct ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": "13511221001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511221001", "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102001_register_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_type值")
    @allure.testcase("FT-HTJK-102-002")
    @pytest.mark.parametrize("client_type, phone, result",
                             [(0, "13511221002", {"code": 1, "msg": ""}), (1, "13511221003", {"code": 1, "msg": ""}),
                              (2, "13511221004", {"code": 1, "msg": ""}), (3, "13511221005", {"code": 1, "msg": ""})],
                             ids=["client_type(0)", "client_type(1)", "client_type(2)", "client_type(3)"])
    def test_102002_clienttype_correct(self, client_type, phone, result):
        """ Test correct client_type values (0, 1, 2, 3) (FT-HTJK-102-002).
        :param client_type: client_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102002_clienttype_correct ({0}) ....".format(client_type))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102002_clienttype_correct ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_type值")
    @allure.testcase("FT-HTJK-102-003")
    @pytest.mark.parametrize("client_type, phone, result",
                             [(-1, "13511221007", {"msg": "", "result": ""}),
                              (4, "13511221008", {"msg": "", "result": ""}),
                              (-2147483649, "13511221009", {"msg": "", "result": ""}),
                              (2147483648, "13511221010", {"msg": "", "result": ""}),
                              (1.0, "13511221011", {"msg": "", "result": ""}),
                              ('a', "13511221012", {"msg": "", "result": ""}),
                              ('中', "13511221013", {"msg": "", "result": ""}),
                              ('*', "13511221014", {"msg": "", "result": ""}),
                              ('1a', "13511221015", {"msg": "", "result": ""}),
                              ('1中', "13511221016", {"msg": "", "result": ""}),
                              ('1*', "13511221017", {"msg": "", "result": ""}),
                              (' ', "13511221018", {"msg": "", "result": ""}),
                              ('', "13511221019", {"msg": "", "result": ""}), ],
                             ids=["client_type(-1)", "client_type(4)", "client_type(超小值)", "client_type(超大值)", "client_type(小数)",
                                  "client_type(字母)", "client_type(中文)", "client_type(特殊字符)", "client_type(数字字母)",
                                  "client_type(数字中文)",
                                  "client_type(数字特殊字符)", "client_type(空格)", "client_type(空)"])
    def test_102003_clienttype_wrong(self, client_type, phone, result):
        """ Test wrong client_type values (-1、4、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-003).
        :param client_type: client_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102003_clienttype_wrong ({0}) ....".format(client_type))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102003_clienttype_wrong ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_version值")
    @allure.testcase("FT-HTJK-102-004")
    @pytest.mark.parametrize("client_version, phone, result",
                             [('1', "13511221020", {"code": 1, "msg": ""}), ('a'*256, "13511221021", {"code": 1, "msg": ""})],
                             ids=["client_version(最小长度值)", "client_version(最大长度值)"])
    def test_102004_clientversion_correct(self, client_version, phone, result):
        """ Test correct client_version values (最小长度值、最大长度值) (FT-HTJK-102-004).
        :param client_version: client_version parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102004_clientversion_correct ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102004_clientversion_correct ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_version值")
    @allure.testcase("FT-HTJK-102-005")
    @pytest.mark.parametrize("client_version, phone, result",
                             [('1'*256, "13511221022", {"msg": "", "result": ""}),
                              ('1.0', "13511221023", {"msg": "", "result": ""}),
                              ('a', "13511221024", {"msg": "", "result": ""}),
                              ('中', "13511221025", {"msg": "", "result": ""}),
                              ('*', "13511221026", {"msg": "", "result": ""}),
                              ('1a', "13511221027", {"msg": "", "result": ""}),
                              ('1中', "13511221028", {"msg": "", "result": ""}),
                              ('1*', "13511221029", {"msg": "", "result": ""}),
                              (' ', "13511221030", {"msg": "", "result": ""}),
                              ('', "13511221031", {"msg": "", "result": ""})],
                             ids=["client_version(超长值)", "client_version(小数)", "client_version(字母)", "client_version(中文)",
                                  "client_version(特殊字符)", "client_version(数字字母)", "client_version(数字中文)",
                                  "client_version(数字特殊字符)", "client_version(空格)", "client_version(空)"])
    def test_102005_clientversion_wrong(self, client_version, phone, result):
        """ Test wrong client_type values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-005).
        :param client_version: client_version parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102005_clientversion_wrong ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102005_clientversion_wrong ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确device_token值")
    @allure.testcase("FT-HTJK-102-006")
    @pytest.mark.parametrize("device_token, phone, result",
                             [('1', "13511221032", {"code": 1, "msg": ""}),
                              ('a' * 256, "13511221033", {"code": 1, "msg": ""})],
                             ids=["device_token(最小长度值)", "device_token(最大长度值)"])
    def test_102006_devicetoken_correct(self, device_token, phone, result):
        """ Test correct device_token values (最小长度值、最大长度值) (FT-HTJK-102-006).
        :param device_token: device_token parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102006_devicetoken_correct ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": device_token,
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102006_devicetoken_correct ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误device_token值")
    @allure.testcase("FT-HTJK-102-007")
    @pytest.mark.parametrize("device_token, phone, result",
                             [('1' * 256, "13511221034", {"msg": "", "result": ""}),
                              ('1.0', "13511221035", {"msg": "", "result": ""}),
                              ('a', "13511221036", {"msg": "", "result": ""}),
                              ('中', "13511221037", {"msg": "", "result": ""}),
                              ('*', "13511221038", {"msg": "", "result": ""}),
                              ('1a', "13511221039", {"msg": "", "result": ""}),
                              ('1中', "13511221040", {"msg": "", "result": ""}),
                              ('1*', "13511221041", {"msg": "", "result": ""}),
                              (' ', "13511221042", {"msg": "", "result": ""}),
                              ('', "13511221043", {"msg": "", "result": ""})],
                             ids=["device_token(超长值)", "device_token(小数)", "device_token(字母)", "device_token(中文)",
                                  "device_token(特殊字符)", "device_token(数字字母)", "device_token(数字中文)",
                                  "device_token(数字特殊字符)", "device_token(空格)", "device_token(空)"])
    def test_102007_devicetoken_wrong(self, device_token, phone, result):
        """ Test wrong device_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-007).
        :param device_token: device_token parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102007_devicetoken_wrong ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": device_token,
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102007_devicetoken_wrong ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确imei值")
    @allure.testcase("FT-HTJK-102-008")
    @pytest.mark.parametrize("imei, phone, result",
                             [('1', "13511221044", {"code": 1, "msg": ""}),
                              ('1' * 256, "13511221045", {"code": 1, "msg": ""})],
                             ids=["imei(最小长度值)", "imei(最大长度值)"])
    def test_102008_imei_correct(self, imei, phone, result):
        """ Test correct imei values (最小长度值、最大长度值) (FT-HTJK-102-008).
        :param imei: imei parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102008_imei_correct ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": imei, "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102008_imei_correct ({0}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误imei值")
    @allure.testcase("FT-HTJK-102-009")
    @pytest.mark.parametrize("imei, phone, result",
                             [('1' * 256, "13511221046", {"msg": "", "result": ""}),
                              ('1.0', "13511221047", {"msg": "", "result": ""}),
                              ('a', "13511221048", {"msg": "", "result": ""}),
                              ('中', "13511221049", {"msg": "", "result": ""}),
                              ('*', "13511221050", {"msg": "", "result": ""}),
                              ('1a', "13511221051", {"msg": "", "result": ""}),
                              ('1中', "13511221052", {"msg": "", "result": ""}),
                              ('1*', "13511221053", {"msg": "", "result": ""}),
                              (' ', "13511221054", {"msg": "", "result": ""}),
                              ('', "13511221055", {"msg": "", "result": ""})],
                             ids=["imei(超长值)", "imei(小数)", "imei(字母)", "imei(中文)",
                                  "imei(特殊字符)", "imei(数字字母)", "imei(数字中文)",
                                  "imei(数字特殊字符)", "imei(空格)", "imei(空)"])
    def test_102009_imei_wrong(self, imei, phone, result):
        """ Test wrong imei values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-009).
        :param imei: imei parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102009_imei_wrong ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": imei, "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102009_imei_wrong ({0}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号码未注册未获取验证码")
    @allure.testcase("FT-HTJK-102-010")
    def test_102010_not_register_no_getmsgcode(self):
        """ Test phone not register no get msg code (FT-HTJK-102-010)."""
        self.logger.info(".... Start test_102010_not_register_no_getmsgcode ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": '13511221056', "code_token": '123456789',
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102010_not_register_no_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号码已注册未获取验证码")
    @allure.testcase("FT-HTJK-102-011")
    def test_102011_register_no_getmsgcode(self):
        """ Test phone register no get msg code (FT-HTJK-102-011)."""
        self.logger.info(".... Start test_102011_register_no_getmsgcode ....")
        try:
            with allure.step("teststep1: register."):
                params = {"code_type": 0, "phone": '13511221057', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                register_result = make_register(self.httpclient, 1, '1.0', '123456789', '46001123456789', 0,
                                                '13511221057', '1234', get_timestamp(), self.logger)
                allure.attach("register_result result", register_result)
                self.logger.info("register_result result: {0}".format(register_result))
                if not register_result:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": '13511221057', "code_token": '123456789',
                        "sms_code": "1235", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102011_register_no_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号码已注册已获取验证码")
    @allure.testcase("FT-HTJK-102-012")
    def test_102012_register_getmsgcode(self):
        """ Test phone register get msg code (FT-HTJK-102-012)."""
        self.logger.info(".... Start test_102012_register_getmsgcode ....")
        try:
            with allure.step("teststep1: register."):
                params = {"code_type": 0, "phone": '13511221058', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                register_result = make_register(self.httpclient, 1, '1.0', '123456789', '46001123456789', 0,
                                                '13511221058', '1234', get_timestamp(), self.logger)
                allure.attach("register_result result", register_result)
                self.logger.info("register_result result: {0}".format(register_result))
                if not register_result:
                    assert False

            with allure.step("teststep2: get msg code."):
                params = {"code_type": 0, "phone": "13511221058", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep3: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": '13511221058', "code_token": '123456789',
                        "sms_code": "1235", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep4: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep5: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102012_register_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-102-013")
    @pytest.mark.parametrize("phone, result",
                             [("1", {"msg": "", "result": ""}),
                              ("135123456789", {"msg": "", "result": ""}),
                              ("0", {"msg": "", "result": ""}),
                              ("-1", {"msg": "", "result": ""}),
                              ("135112210.0", {"msg": "", "result": ""}),
                              ("1"*256, {"msg": "", "result": ""}),
                              ("a", {"msg": "", "result": ""}),
                              ("中", {"msg": "", "result": ""}),
                              ("*", {"msg": "", "result": ""}),
                              ("1351122105a", {"msg": "", "result": ""}),
                              ("1351122105中", {"msg": "", "result": ""}),
                              ("1351122105*", {"msg": "", "result": ""}),
                              (" ", {"msg": "", "result": ""}),
                              ("", {"msg": "", "result": ""})],
                             ids=["phone(1)", "phone(12位)", "phone(0)", "phone(-1)", "phone(小数)", "phone(超长值)",
                                  "phone(字母)", "phone(中文)", "phone(特殊字符)", "phone(数字字母)", "phone(数字中文)",
                                  "phone(数字特殊字符)", "phone(空格)", "phone(空)"])
    def test_102013_phone_wrong(self, phone, result):
        """ Test wrong phone values (1、12位、0、-1、小数、超长值、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-009).
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102013_phone_wrong ({0}) ....".format(phone))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102013_phone_wrong ({0}) ....".format(phone))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_token值")
    @allure.testcase("FT-HTJK-102-014")
    @pytest.mark.parametrize("code_token, phone, result",
                             [('1' * 256, "13511221059", {"msg": "", "result": ""}),
                              ('1.0', "13511221060", {"msg": "", "result": ""}),
                              ('a', "13511221061", {"msg": "", "result": ""}),
                              ('中', "13511221062", {"msg": "", "result": ""}),
                              ('*', "13511221063", {"msg": "", "result": ""}),
                              ('1a', "13511221064", {"msg": "", "result": ""}),
                              ('1中', "13511221065", {"msg": "", "result": ""}),
                              ('1*', "13511221066", {"msg": "", "result": ""}),
                              (' ', "13511221067", {"msg": "", "result": ""}),
                              ('', "13511221068", {"msg": "", "result": ""})],
                             ids=["code_token(超长值)", "code_token(小数)", "code_token(字母)", "code_token(中文)",
                                  "code_token(特殊字符)", "code_token(数字字母)", "code_token(数字中文)",
                                  "code_token(数字特殊字符)", "code_token(空格)", "code_token(空)"])
    def test_102014_codetoken_wrong(self, code_token, phone, result):
        """ Test wrong code_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-014).
        :param code_token: code_token parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102014_codetoken_wrong ({0}) ....".format(code_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token1)
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                if not code_token1:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102014_codetoken_wrong ({0}) ....".format(code_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误sms_code值")
    @allure.testcase("FT-HTJK-102-015")
    @pytest.mark.parametrize("sms_code, phone, result",
                             [('1' * 256, "13511221069", {"msg": "", "result": ""}),
                              ('1.0', "13511221070", {"msg": "", "result": ""}),
                              ('a', "13511221071", {"msg": "", "result": ""}),
                              ('中', "13511221072", {"msg": "", "result": ""}),
                              ('*', "13511221073", {"msg": "", "result": ""}),
                              ('1a', "13511221074", {"msg": "", "result": ""}),
                              ('1中', "13511221075", {"msg": "", "result": ""}),
                              ('1*', "13511221076", {"msg": "", "result": ""}),
                              (' ', "13511221077", {"msg": "", "result": ""}),
                              ('', "13511221078", {"msg": "", "result": ""})],
                             ids=["sms_code(超长值)", "sms_code(小数)", "sms_code(字母)", "sms_code(中文)",
                                  "sms_code(特殊字符)", "sms_code(数字字母)", "sms_code(数字中文)",
                                  "sms_code(数字特殊字符)", "sms_code(空格)", "sms_code(空)"])
    def test_102015_smscode_wrong(self, sms_code, phone, result):
        """ Test wrong sms_code values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-015).
        :param sms_code: sms_code parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102015_smscode_wrong ({0}) ....".format(sms_code))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": sms_code, "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102015_smscode_wrong ({0}) ....".format(sms_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-102-016")
    @pytest.mark.parametrize("timestamp, phone, result",
                             [(get_timestamp() - 1000, "13511221079", {"code": 1, "msg": ""}),
                              (get_timestamp() + 1000, "13511221080", {"code": 1, "msg": ""})],
                             ids=["timestamp(最小长度值)", "timestamp(最大长度值)"])
    def test_102016_timestamp_correct(self, timestamp, phone, result):
        """ Test correct timestamp values (最小值、最大值) (FT-HTJK-102-016).
        :param timestamp: timestamp parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102016_timestamp_correct ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": timestamp}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102016_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-102-017")
    @pytest.mark.parametrize("timestamp, phone, result",
                             [(1, "13511221081", {"msg": "", "result": ""}),
                              (9223372036854775807, "13511221082", {"msg": "", "result": ""}),
                              (0, "13511221083", {"msg": "", "result": ""}),
                              (-1, "13511221084", {"msg": "", "result": ""}),
                              (-9223372036854775809, "13511221085", {"msg": "", "result": ""}),
                              (9223372036854775808, "13511221086", {"msg": "", "result": ""}),
                              (1.0, "13511221087", {"msg": "", "result": ""}),
                              ('a', "13511221088", {"msg": "", "result": ""}),
                              ('中', "13511221089", {"msg": "", "result": ""}),
                              ('*', "13511221090", {"msg": "", "result": ""}),
                              ('1a', "13511221091", {"msg": "", "result": ""}),
                              ('1中', "13511221092", {"msg": "", "result": ""}),
                              ('1*', "13511221093", {"msg": "", "result": ""}),
                              (' ', "13511221094", {"msg": "", "result": ""}),
                              ('', "13511221095", {"msg": "", "result": ""}), ],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_102017_timestamp_wrong(self, timestamp, phone, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-102-003).
        :param timestamp: timestamp parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102017_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "1234", "timestamp": timestamp}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102017_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_type参数")
    @allure.testcase("FT-HTJK-102-018")
    def test_102018_no_clienttype(self):
        """ Test register without client_type(FT-HTJK-102-018)."""
        self.logger.info(".... Start test_102018_no_clienttype ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221096', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221096', "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102018_no_clienttype ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_version参数")
    @allure.testcase("FT-HTJK-102-019")
    def test_102019_no_clientversion(self):
        """ Test register without client_version(FT-HTJK-102-019)."""
        self.logger.info(".... Start test_102019_no_clientversion ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221097', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221097', "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102019_no_clientversion ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_token参数")
    @allure.testcase("FT-HTJK-102-020")
    def test_102020_no_devicetoken(self):
        """ Test register without device_token(FT-HTJK-102-020)."""
        self.logger.info(".... Start test_102020_no_devicetoken ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221098', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1",
                        "imei": "460011234567890", "phone": '13511221098', "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102020_no_devicetoken ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少imei参数")
    @allure.testcase("FT-HTJK-102-021")
    def test_102021_no_imei(self):
        """ Test register without imei(FT-HTJK-102-021)."""
        self.logger.info(".... Start test_102021_no_imei ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221099', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "phone": '13511221099', "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102021_no_imei ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少phone参数")
    @allure.testcase("FT-HTJK-102-022")
    def test_102022_no_phone(self):
        """ Test register without phone(FT-HTJK-102-022)."""
        self.logger.info(".... Start test_102022_no_phone ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221100', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "code_token": code_token,
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102022_no_phone ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少code_token参数")
    @allure.testcase("FT-HTJK-102-023")
    def test_102023_no_code_token(self):
        """ Test register without code_token(FT-HTJK-102-023)."""
        self.logger.info(".... Start test_102023_no_code_token ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221101', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221101',
                        "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102023_no_code_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少sms_code参数")
    @allure.testcase("FT-HTJK-102-024")
    def test_102024_no_sms_code(self):
        """ Test register without sms_code(FT-HTJK-102-024)."""
        self.logger.info(".... Start test_102024_no_sms_code ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221102', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221102', "code_token": code_token,
                        "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102024_no_sms_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-102-025")
    def test_102025_no_timestamp(self):
        """ Test register without timestamp(FT-HTJK-102-025)."""
        self.logger.info(".... Start test_102025_no_timestamp ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": '13511221103', "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", params)
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", code_token)
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221103', "code_token": code_token,
                        "sms_code": "1234"}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102025_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-v', '-k', '102025', 'test_Register.py'])
    # pytest.main(['-v', 'test_Register.py::TestRegister::test_102025_no_timestamp'])
