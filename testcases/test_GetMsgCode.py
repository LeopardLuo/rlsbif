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


@allure.feature("注册-获取验证码")
class TestGetMsgCode(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'GetMsgCode')
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
    @allure.story("获取正确验证码")
    @allure.testcase("FT-HTJK-101-001")
    def test_101001_get_correct_msg_code(self):
        """ Test get the correct msg code by correct parameters(FT-HTJK-101-001)."""
        self.logger.info(".... Start test_101001_get_correct_msg_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": "13511220001", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["code_token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101001_get_correct_msg_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确code_type值")
    @allure.testcase("FT-HTJK-101-002")
    @pytest.mark.parametrize("code_type, phone, result",
                             [(0, "13511220002", {"code": 1, "msg": ""}), (1, "13511220003", {"code": 1, "msg": ""}),
                              (2, "13511220004", {"code": 1, "msg": ""}), (3, "13511220005", {"code": 1, "msg": ""}),
                              (4, "13511220006", {"code": 1, "msg": ""})],
                             ids=["code_type(0)", "code_type(1)", "code_type(2)", "code_type(3)", "code_type(4)"])
    def test_101002_codetype_correct(self, code_type, phone, result):
        """ Test correct code_type values (0, 1, 2, 3, 4) (FT-HTJK-101-002).
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101002_codetype_correct ({0}) ....".format(code_type))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": code_type, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == result['code']
                assert rsp_content["msg"] == result['msg']
                assert len(rsp_content["result"]["code_token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101002_codetype_correct ({0}) ....".format(code_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_type值")
    @allure.testcase("FT-HTJK-101-003")
    @pytest.mark.parametrize("code_type, phone, result",
                             [(-1, "13511220007", {"msg": "", "result": ""}), (5, "13511220008", {"msg": "", "result": ""}),
                              (-2147483649, "13511220009", {"msg": "", "result": ""}), (2147483648, "13511220010", {"msg": "", "result": ""}),
                              (1.0, "13511220011", {"msg": "", "result": ""}), ('a', "13511220012", {"msg": "", "result": ""}),
                              ('中', "13511220013", {"msg": "", "result": ""}), ('*', "13511220014", {"msg": "", "result": ""}),
                              ('1a', "13511220015", {"msg": "", "result": ""}), ('1中', "13511220016", {"msg": "", "result": ""}),
                              ('1*', "13511220017", {"msg": "", "result": ""}), (' ', "13511220018", {"msg": "", "result": ""}),
                              ('', "13511220019", {"msg": "", "result": ""}),],
                             ids=["code_type(-1)", "code_type(5)", "code_type(超小值)", "code_type(超大值)", "code_type(小数)",
                                  "code_type(字母)", "code_type(中文)", "code_type(特殊字符)", "code_type(数字字母)", "code_type(数字中文)",
                                  "code_type(数字特殊字符)", "code_type(空格)", "code_type(空)"])
    def test_101003_codetype_wrong(self, code_type, phone, result):
        """ Test wrong code_type values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-101-003).
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101003_codetype_wrong ({0}) ....".format(code_type))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": code_type, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert rsp_content["msg"] == result['msg']
                assert rsp_content["result"] == result['result']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101003_codetype_wrong ({0}) ....".format(code_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号码未注册")
    @allure.testcase("FT-HTJK-101-004")
    def test_101004_phone_not_register(self):
        """ Test get the msg code using phone not register(FT-HTJK-101-004)."""
        self.logger.info(".... Start test_101004_phone_not_register ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": "13511220020", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == 1
                assert len(rsp_content["msg"]) == 0
                assert len(rsp_content["result"]["code_token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101004_phone_not_register ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号码已注册")
    @allure.testcase("FT-HTJK-101-005")
    def test_101005_phone_has_registered(self):
        """ Test get the msg code using phone registered(FT-HTJK-101-005)."""
        self.logger.info(".... Start test_101005_phone_has_registered ....")
        try:
            with allure.step("teststep1: register first."):
                params = {"code_type": 0, "phone": "13511220021", "client_type": 1, "client_version": "0.1",
                          "device_token": "1234567890", "imei": "460011234567890", "sms_code": "1234", "timestamp": get_timestamp()}
                allure.attach("params value", params)
                self.logger.info("params: {0}".format(params))
                register_result = make_register(self.httpclient, params["client_type"], params["client_version"],
                                                params["device_token"], params["imei"], params["code_type"], params["phone"],
                                                params["sms_code"], params["timestamp"], logger=self.logger)
                allure.attach("Register result:", register_result)
                self.logger.info("Register result: {0}".format(register_result))
                if not register_result:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"code_type": 0, "phone": "13511220021", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) != 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101005_phone_has_registered ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-101-006")
    @pytest.mark.parametrize("code_type, phone, result",
                             [(0, "-1", {"msg": "", "result": ""}),
                              (0, "135123456789", {"msg": "", "result": ""}),
                              (0, "0", {"msg": "", "result": ""}),
                              (0, "1", {"msg": "", "result": ""}),
                              (0, "1351234567.0", {"msg": "", "result": ""}),
                              (0, "13511220012"*10, {"msg": "", "result": ""}),
                              (0, "abcdefghijk", {"msg": "", "result": ""}),
                              (0, "中"*11, {"msg": "", "result": ""}),
                              (0, "*"*11, {"msg": "", "result": ""}),
                              (0, "1351122001a", {"msg": "", "result": ""}),
                              (0, "1351122001中", {"msg": "", "result": ""}),
                              (0, "1351122001*", {"msg": "", "result": ""}),
                              (0, " "*11, {"msg": "", "result": ""}),
                              (0, "", {"msg": "", "result": ""}),],
                             ids=["phone(-1)", "phone(135123456789)", "phone(0)", "phone(1)", "phone(小数)",
                                  "phone(超长)","phone(字母)", "phone(中文)", "phone(特殊字符)", "phone(数字字母)",
                                  "phone(数字中文)", "phone(数字特殊字符)", "phone(空格)", "phone(空)"])
    def test_101006_phone_wrong(self, code_type, phone, result):
        """ Test wrong phone values (-1、135123456789、0、1、1351234567.0、超长、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-101-006).
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101006_phone_wrong ({0}) ....".format(phone))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": code_type, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert rsp_content["msg"] == result['msg']
                assert rsp_content["result"] == result['result']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101006_phone_wrong ({0}) ....".format(phone))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确时间戳值")
    @allure.testcase("FT-HTJK-101-007")
    @pytest.mark.parametrize("phone, timestamp, result",
                             [("13511220022", get_timestamp() - 1000, {"code": 1, "msg": ""}),
                              ("13511220023", get_timestamp() + 1000, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_101007_timestamp_correct(self, phone, timestamp, result):
        """ Test correct timestamp values (最小值、最大值) (FT-HTJK-101-007).
        :param phone: phone parameter value.
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101007_timestamp_correct ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": phone, "timestamp": timestamp}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == result['code']
                assert rsp_content["msg"] == result['msg']
                assert len(rsp_content["result"]["code_token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101007_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误时间戳值")
    @allure.testcase("FT-HTJK-101-008")
    @pytest.mark.parametrize("phone, timestamp, result",
                             [("13511220024", "-1", {"msg": "", "result": ""}),
                              ("13511220025", "9223372036854775807", {"msg": "", "result": ""}),
                              ("13511220026", "0", {"msg": "", "result": ""}),
                              ("13511220027", "1", {"msg": "", "result": ""}),
                              ("13511220028", "-9223372036854775809", {"msg": "", "result": ""}),
                              ("13511220029", "9223372036854775808", {"msg": "", "result": ""}),
                              ("13511220030", "1.0", {"msg": "", "result": ""}),
                              ("13511220031", "a", {"msg": "", "result": ""}),
                              ("13511220032", "中", {"msg": "", "result": ""}),
                              ("13511220033", "*", {"msg": "", "result": ""}),
                              ("13511220034", "1351122a", {"msg": "", "result": ""}),
                              ("13511220035", "1351122中", {"msg": "", "result": ""}),
                              ("13511220036", "1351122*", {"msg": "", "result": ""}),
                              ("13511220037", " ", {"msg": "", "result": ""}),
                              ("13511220038", "", {"msg": "", "result": ""}), ],
                             ids=["timestamp(-1)", "timestamp(最大值)", "timestamp(0)", "timestamp(1)", "timestamp(超小值)",
                                  "timestamp(超大值)", "timestamp(小数)", "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)", "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_101008_timestamp_wrong(self, phone, timestamp, result):
        """ Test wrong phone values (-1、135123456789、0、1、1351234567.0、超长、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-101-006).
        :param phone: phone parameter value.
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101008_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": phone, "timestamp": timestamp}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert rsp_content["msg"] == result['msg']
                assert rsp_content["result"] == result['result']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101008_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少code_type参数")
    @allure.testcase("FT-HTJK-101-009")
    def test_101009_no_code_type(self):
        """ Test get the msg code without code_type(FT-HTJK-101-009)."""
        self.logger.info(".... Start test_101009_no_code_type ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"phone": "13511220039", "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101009_no_code_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少phone参数")
    @allure.testcase("FT-HTJK-101-010")
    def test_101010_no_phone(self):
        """ Test get the msg code without phone(FT-HTJK-101-010)."""
        self.logger.info(".... Start test_101010_no_phone ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "timestamp": get_timestamp()}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101010_no_phone ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少时间戳参数")
    @allure.testcase("FT-HTJK-101-011")
    def test_101011_no_timestamp(self):
        """ Test get the msg code without timestamp(FT-HTJK-101-011)."""
        self.logger.info(".... Start test_101011_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": "13511220040",}
                allure.attach("params value", json)
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 400
                assert rsp_content["code"] != 1
                assert len(rsp_content["msg"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101011_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_template.py'])
