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

    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'GetMsgCode')
                allure.attach("uri", "{0}".format(cls.URI))
                cls.logger.info("uri: " + cls.URI)
            with allure.step("初始化HTTP客户端。"):
                sv_protocol = cls.config.getItem('server', 'protocol')
                sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(sv_protocol, sv_host, sv_port)
                allure.attach("baseurl", "{0}".format(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)
            with allure.step("初始化数据库连接。"):
                db_user = cls.config.getItem('db', 'db_user')
                db_password = cls.config.getItem('db', 'db_password')
                db_host = cls.config.getItem('db', 'db_host')
                db_database = cls.config.getItem('db', 'db_database')
                db_port = int(cls.config.getItem('db', 'db_port'))
                allure.attach("db_params", "{0},{1},{2},{3},{4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)

            with allure.step("delete register user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", "{0}".format(table))
                cls.logger.info("table: {0}".format(table))
                delete_result = cls.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", "{0}".format(delete_result))
                cls.logger.info("delete result: {0}".format(delete_result))
        except Exception as e:
            cls.logger.error("Error: there is exception occur:")
            cls.logger.error(e)
            assert False
        cls.logger.info("*** End setup class ***")
        cls.logger.info("")

    def teardown_class(cls):
        cls.logger.info("")
        cls.logger.info("*** Start teardown class ***")
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
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
    @allure.story("获取正确验证码")
    @allure.testcase("FT-HTJK-101-001")
    def test_101001_get_correct_msg_code(self):
        """ Test get the correct msg code by correct parameters(FT-HTJK-101-001)."""
        self.logger.info(".... Start test_101001_get_correct_msg_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": "13511220001", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '短信已下发' in rsp_content["message"]
                assert len(rsp_content["result"]["code_token"]) > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                             [(0, "13511220002", {"code": 1, "msg": "短信已下发"}), (1, "13511220003", {"code": 1, "msg": "短信已下发"}),
                              (2, "13511220004", {"code": 1, "msg": "短信已下发"}), (3, "13511220005", {"code": 1, "msg": "短信已下发"}),
                              (4, "13511220006", {"code": 0, "msg": "手机号码不存在"})],
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                             [(-1, "13511220007", {"status": 200, "msg": "code_type值非法", "code": 0}),
                              (5, "13511220008", {"status": 200, "msg": "code_type值非法", "code": 0}),
                              (-2147483649, "13511220009", {"status": 400, "msg": "", "code": ""}),
                              (2147483648, "13511220010", {"status": 400, "msg": "", "code": ""}),
                              (1.0, "13511220011", {"status": 400, "msg": "", "code": ""}),
                              ('a', "13511220012", {"status": 400, "msg": "", "code": ""}),
                              ('中', "13511220013", {"status": 400, "msg": "", "code": ""}),
                              ('*', "13511220014", {"status": 400, "msg": "", "code": ""}),
                              ('1a', "13511220015", {"status": 400, "msg": "", "code": ""}),
                              ('1中', "13511220016", {"status": 400, "msg": "", "code": ""}),
                              ('1*', "13511220017", {"status": 400, "msg": "", "code": ""}),
                              (' ', "13511220018", {"status": 400, "msg": "", "code": ""}),
                              ('', "13511220019", {"status": 400, "msg": "", "code": ""}),],
                             ids=["code_type(-1)", "code_type(5)", "code_type(超小值)", "code_type(超大值)", "code_type(小数)",
                                  "code_type(字母)", "code_type(中文)", "code_type(特殊字符)", "code_type(数字字母)", "code_type(数字中文)",
                                  "code_type(数字特殊字符)", "code_type(空格)", "code_type(空)"])
    def test_101003_codetype_wrong(self, code_type, phone, result):
        """ Test wrong code_type values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、
            数字特殊字符、空格、空）(FT-HTJK-101-003).
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101003_codetype_wrong ({0}) ....".format(code_type))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": code_type, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']

            with allure.step("teststep3: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if result['status'] == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content['code_type']
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == 1
                assert '短信已下发' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                          "device_token": "1234567890", "imei": "460011234567890", "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("params: {0}".format(params))
                register_result = make_register(self.httpclient, params["client_type"], params["client_version"],
                                                params["device_token"], params["imei"], params["code_type"], params["phone"],
                                                params["sms_code"], params["timestamp"], logger=self.logger)
                allure.attach("Register result:", "{0}".format(register_result))
                self.logger.info("Register result: {0}".format(register_result))
                if not register_result:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"code_type": 0, "phone": "13511220021", "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", "{0}".format(rsp.request.headers))
                allure.attach("request.body", "{0}".format(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", "{0}".format(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200

            with allure.step("teststep5: assert the response content"):
                rsp_content = rsp.json()
                allure.attach("response content：", "{0}".format(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '手机号码已注册' in rsp_content["message"]

            with allure.step("teststep6: verify phone."):
                json = {"code_type": 4, "phone": "13511220021", "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(json))
                self.logger.info("params: {0}".format(json))
                rsp = self.httpclient.post(self.URI, json=json)
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", "{0}".format(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '短信已下发' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101005_phone_has_registered ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-101-006")
    @pytest.mark.parametrize("phone, result",
                             [("-1", {"msg": "手机号码格式不正确", "code": 0}),
                              ("135123456789", {"msg": "手机号码格式不正确", "code": 0}),
                              ("0", {"msg": "手机号码格式不正确", "code": 0}),
                              ("1", {"msg": "手机号码格式不正确", "code": 0}),
                              ("1351234567.0", {"msg": "手机号码格式不正确", "code": 0}),
                              ("13511220012"*10, {"msg": "手机号码格式不正确", "code": 0}),
                              ("abcdefghijk", {"msg": "手机号码格式不正确", "code": 0}),
                              ("中"*11, {"msg": "手机号码格式不正确", "code": 0}),
                              ("*"*11, {"msg": "手机号码格式不正确", "code": 0}),
                              ("1351122001a", {"msg": "手机号码格式不正确", "code": 0}),
                              ("1351122001中", {"msg": "手机号码格式不正确", "code": 0}),
                              ("1351122001*", {"msg": "手机号码格式不正确", "code": 0}),
                              (" "*11, {"msg": "手机号码格式不正确", "code": 0}),
                              ("", {"msg": "手机号码格式不正确", "code": 0})],
                             ids=["phone(-1)", "phone(135123456789)", "phone(0)", "phone(1)", "phone(小数)",
                                  "phone(超长)","phone(字母)", "phone(中文)", "phone(特殊字符)", "phone(数字字母)",
                                  "phone(数字中文)", "phone(数字特殊字符)", "phone(空格)", "phone(空)"])
    def test_101006_phone_wrong(self, phone, result):
        """ Test wrong phone values (-1、135123456789、0、1、1351234567.0、超长、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-101-006).
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_101006_phone_wrong ({0}) ....".format(phone))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200

            with allure.step("teststep4: assert the response content"):
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert not rsp_content["result"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                             [("13511220022", 1, {"code": 1, "msg": ""}),
                              ("13511220023", get_timestamp() + 10000, {"code": 1, "msg": ""})],
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200

            with allure.step("teststep3: assert the response content"):
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert rsp_content["result"]["code_token"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                             [("13511220024", -1, {"status": 200, "msg": "不正确", "code": 0}),
                              ("13511220025", 9223372036854775807, {"status": 200, "msg": "不正确", "code": 0}),
                              ("13511220026", 0, {"status": 200, "msg": "不正确", "code": 0}),
                              ("13511220027", 1, {"status": 200, "msg": "不正确", "code": 0}),
                              ("13511220028", -9223372036854775809, {"status": 400, "msg": "", "code": ""}),
                              ("13511220029", 9223372036854775808, {"status": 400, "msg": "", "code": ""}),
                              ("13511220030", 1.0, {"status": 400, "msg": "", "code": ""}),
                              ("13511220031", "a", {"status": 400, "msg": "", "code": ""}),
                              ("13511220032", "中", {"status": 400, "msg": "", "code": ""}),
                              ("13511220033", "*", {"status": 400, "msg": "", "code": ""}),
                              ("13511220034", "1351122a", {"status": 400, "msg": "", "code": ""}),
                              ("13511220035", "1351122中", {"status": 400, "msg": "", "code": ""}),
                              ("13511220036", "1351122*", {"status": 400, "msg": "", "code": ""}),
                              ("13511220037", " ", {"status": 400, "msg": "", "code": ""}),
                              ("13511220038", "", {"status": 400, "msg": "", "code": ""})],
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']

            with allure.step("teststep3: assert the response content"):
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if result['status'] == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content["timestamp"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == 0
                assert "不能为空" in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == 0
                assert "不能为空" in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
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
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                rsp_content = rsp.json()
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp.status_code == 200
                assert rsp_content["code"] == 0
                assert "不能为空" in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_101011_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_GetMsgCode.py'])
    pytest.main(['-s', 'test_APP_GetMsgCode.py::TestGetMsgCode::test_101001_get_correct_msg_code'])
