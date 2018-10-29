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


@allure.feature("APP-注册-完成注册")
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
                allure.attach("db_params", "{0},{1},{2},{3},{4},".format(db_user, db_password, db_host, db_database, db_port))
                cls.logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
                cls.mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)

            with allure.step("delete register user info"):
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
    @allure.story("注册成功")
    @allure.testcase("FT-HTJK-102-001")
    def test_102001_register_correct(self):
        """ Test register by correct parameters(FT-HTJK-102-001)."""
        self.logger.info(".... Start test_102001_register_correct ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": "13511221001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511221001", "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '登录成功' in rsp_content["message"]
                assert rsp_content["result"]["token"]
                assert rsp_content["result"]["user_info"]["member_id"]
                assert rsp_content["result"]["user_info"]["user_name"] == json['phone']
                assert rsp_content["result"]["user_info"]["nickname"] == json['phone']
                assert rsp_content["result"]["user_info"]["phone"] == json['phone']
                assert rsp_content["result"]["user_info"]["sex"] == 3
                assert not rsp_content["result"]["user_info"]["province"]
                assert not rsp_content["result"]["user_info"]["city"]
                assert not rsp_content["result"]["user_info"]["district"]
                assert not rsp_content["result"]["user_info"]["address"]
                assert rsp_content["result"]["user_info"]["state"] == 0
                assert rsp_content["result"]["user_info"]["auth_state"] == 0

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"], get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102001_register_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_type值")
    @allure.testcase("FT-HTJK-102-002")
    @pytest.mark.parametrize("client_type, phone, result",
                             [(0, "13511221002", {"code": 1, "msg": "登录成功"}), (1, "13511221003", {"code": 1, "msg": "登录成功"}),
                              (2, "13511221004", {"code": 1, "msg": "登录成功"}), (3, "13511221005", {"code": 1, "msg": "登录成功"})],
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"], get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102002_clienttype_correct ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_type值")
    @allure.testcase("FT-HTJK-102-003")
    @pytest.mark.parametrize("client_type, phone, result",
                             [(-1, "13511221007", {"status": 200, "msg": "client_type值非法", "code": 0}),
                              (4, "13511221008", {"status": 200, "msg": "client_type值非法", "code": 0}),
                              (-2147483649, "13511221009", {"status": 400, "msg": "", "code": 0}),
                              (2147483648, "13511221010", {"status": 400, "msg": "", "code": 0}),
                              (1.0, "13511221011", {"status": 400, "msg": "", "code": 0}),
                              ('a', "13511221012", {"status": 400, "msg": "", "code": 0}),
                              ('中', "13511221013", {"status": 400, "msg": "", "code": 0}),
                              ('*', "13511221014", {"status": 400, "msg": "", "code": 0}),
                              ('1a', "13511221015", {"status": 400, "msg": "", "code": 0}),
                              ('1中', "13511221016", {"status": 400, "msg": "", "code": 0}),
                              ('1*', "13511221017", {"status": 400, "msg": "", "code": 0}),
                              (' ', "13511221018", {"status": 400, "msg": "", "code": 0}),
                              ('', "13511221019", {"status": 400, "msg": "", "code": 0})],
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result["status"]
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if result["status"] == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                                   get_timestamp(), self.logger)
                            allure.attach("logout result：", str(logout_result))
                            self.logger.info("logout result: {}".format(logout_result))
                            self.httpclient.update_header({"authorization": ""})
                    assert rsp_content["code"] == result["code"]
                    assert result["msg"] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102003_clienttype_wrong ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_version值")
    @allure.testcase("FT-HTJK-102-004")
    @pytest.mark.parametrize("client_version, phone, result",
                             [('1' * 50, "13511221022", {"msg": "登录成功", "code": 1}),
                              ('1.0', "13511221023", {"msg": "登录成功", "code": 1}),
                              ('a', "13511221024", {"msg": "登录成功", "code": 1}),
                              ('中', "13511221025", {"msg": "登录成功", "code": 1}),
                              ('*', "13511221026", {"msg": "登录成功", "code": 1}),
                              ('1a', "13511221027", {"msg": "登录成功", "code": 1}),
                              ('1中', "13511221028", {"msg": "登录成功", "code": 1}),
                              ('1*', "13511221029", {"msg": "登录成功", "code": 1})],
                             ids=["client_version(最大长度值)", "client_version(小数)", "client_version(字母)",
                                  "client_version(中文)", "client_version(特殊字符)", "client_version(数字字母)",
                                  "client_version(数字中文)", "client_version(数字特殊字符)"])
    def test_102004_clientversion_correct(self, client_version, phone, result):
        """ Test correct client_version values (最大长度值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符) (FT-HTJK-102-004).
        :param client_version: client_version parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102004_clientversion_correct ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102004_clientversion_correct ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_version值")
    @allure.testcase("FT-HTJK-102-005")
    @pytest.mark.parametrize("client_version, phone, result",
                             [('1'*1001, "13511221020", {"status": 200, "msg": "", "code": 0}),
                              (' ', "13511221030", {"status": 200, "msg": "client_version不能为空", "code": 0}),
                              ('', "13511221031", {"status": 200, "msg": "client_version不能为空", "code": 0})],
                             ids=["client_version(超长值)", "client_version(空格)", "client_version(空)"])
    def test_102005_clientversion_wrong(self, client_version, phone, result):
        """ Test wrong client_type values (超长值、数字、空格、空）(FT-HTJK-102-005).
        :param client_version: client_version parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102005_clientversion_wrong ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result["status"]
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if result["status"] == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                                   get_timestamp(), self.logger)
                            allure.attach("logout result：", str(logout_result))
                            self.logger.info("logout result: {}".format(logout_result))
                            self.httpclient.update_header({"authorization": ""})
                    assert rsp_content["code"] == result["code"]
                    assert result["msg"] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102005_clientversion_wrong ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确device_token值")
    @allure.testcase("FT-HTJK-102-006")
    @pytest.mark.parametrize("device_token, phone, result",
                             [('1' * 100, "13511221034", {"msg": "登录成功", "code": 1}),
                              ('1.0', "13511221035", {"msg": "登录成功", "code": 1}),
                              ('a', "13511221036", {"msg": "登录成功", "code": 1}),
                              ('中', "13511221037", {"msg": "登录成功", "code": 1}),
                              ('*', "13511221038", {"msg": "登录成功", "code": 1}),
                              ('1a', "13511221039", {"msg": "登录成功", "code": 1}),
                              ('1中', "13511221040", {"msg": "登录成功", "code": 1}),
                              ('1*', "13511221041", {"msg": "登录成功", "code": 1})],
                             ids=["device_token(最大长度值)", "device_token(小数)", "device_token(字母)", "device_token(中文)",
                                  "device_token(特殊字符)", "device_token(数字字母)", "device_token(数字中文)",
                                  "device_token(数字特殊字符)"])
    def test_102006_devicetoken_correct(self, device_token, phone, result):
        """ Test correct device_token values (最大长度值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符) (FT-HTJK-102-006).
        :param device_token: device_token parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102006_devicetoken_correct ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": device_token,
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102006_devicetoken_correct ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误device_token值")
    @allure.testcase("FT-HTJK-102-007")
    @pytest.mark.parametrize("device_token, phone, result",
                             [('a' * 101, "13511221033", {"code": 0, "msg": "用户注册失败"}),
                              (' ', "13511221042", {"code": 0, "msg": "device_token不能为空"}),
                              ('', "13511221043", {"code": 0, "msg": "device_token不能为空"})],
                             ids=["device_token(超长值)", "device_token(空格)", "device_token(空)"])
    def test_102007_devicetoken_wrong(self, device_token, phone, result):
        """ Test wrong device_token values (超长值、空格、空）(FT-HTJK-102-007).
        :param device_token: device_token parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102007_devicetoken_wrong ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": device_token,
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                                   get_timestamp(), self.logger)
                            allure.attach("logout result：", str(logout_result))
                            self.logger.info("logout result: {}".format(logout_result))
                            self.httpclient.update_header({"authorization": ""})
                    assert rsp_content["code"] == result["code"]
                    assert result["msg"] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102007_devicetoken_wrong ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确imei值")
    @allure.testcase("FT-HTJK-102-008")
    @pytest.mark.parametrize("imei, phone, result",
                             [('1' * 15, "13511221046", {"code": 1, "msg": "登录成功"}),
                              ('1.0', "13511221047", {"code": 1, "msg": "登录成功"}),
                              ('a', "13511221048", {"code": 1, "msg": "登录成功"}),
                              ('中', "13511221049", {"code": 1, "msg": "登录成功"}),
                              ('*', "13511221050", {"code": 1, "msg": "登录成功"}),
                              ('1a', "13511221051", {"code": 1, "msg": "登录成功"}),
                              ('1中', "13511221052", {"code": 1, "msg": "登录成功"}),
                              ('1*', "13511221053", {"code": 1, "msg": "登录成功"})],
                             ids=["imei(超长值)", "imei(小数)", "imei(字母)", "imei(中文)",
                                  "imei(特殊字符)", "imei(数字字母)", "imei(数字中文)",
                                  "imei(数字特殊字符)"])
    def test_102008_imei_correct(self, imei, phone, result):
        """ Test correct imei values (最大长度值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符) (FT-HTJK-102-008).
        :param imei: imei parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102008_imei_correct ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": imei, "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102008_imei_correct ({0}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误imei值")
    @allure.testcase("FT-HTJK-102-009")
    @pytest.mark.parametrize("imei, phone, result",
                             [('1' * 16, "13511221045", {"code": 0, "msg": "用户注册失败"}),
                              (' ', "13511221054", {"code": 0, "msg": "imei不能为空"}),
                              ('', "13511221055", {"code": 0, "msg": "imei不能为空"})],
                             ids=["imei(超长值)", "imei(空格)", "imei(空)"])
    def test_102009_imei_wrong(self, imei, phone, result):
        """ Test wrong imei values (超长值、空格、空）(FT-HTJK-102-009).
        :param imei: imei parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_102009_imei_wrong ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 0, "phone": phone, "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": imei, "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                                   get_timestamp(), self.logger)
                            allure.attach("logout result：", str(logout_result))
                            self.logger.info("logout result: {}".format(logout_result))
                            self.httpclient.update_header({"authorization": ""})
                    assert rsp_content["code"] == result["code"]
                    assert result["msg"] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                        "sms_code": "123456", "timestamp": get_timestamp()}
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
                self.logger.info("response code: {}".format(rsp.status_code))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                register_result = make_register(self.httpclient, 1, '1.0', '123456789', '46001123456789', 0,
                                                '13511221057', '123456', get_timestamp(), self.logger)
                allure.attach("register_result result", str(register_result))
                self.logger.info("register_result result: {0}".format(register_result))
                if not register_result:
                    assert False
                self.httpclient.update_header({"authorization": register_result["token"]})
                logout_result = logout(self.httpclient, register_result["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": '13511221057', "code_token": '123456789',
                        "sms_code": "123556", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                register_result = make_register(self.httpclient, 1, '1.0', '123456789', '46001123456789', 0,
                                                '13511221058', '123456', get_timestamp(), self.logger)
                allure.attach("register_result result", str(register_result))
                self.logger.info("register_result result: {0}".format(register_result))
                if not register_result:
                    assert False
                self.httpclient.update_header({"authorization": register_result["token"]})
                logout_result = logout(self.httpclient, register_result["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})

            with allure.step("teststep2: get msg code."):
                params = {"code_type": 0, "phone": "13511221058", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert not code_token
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102012_register_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-102-013")
    @pytest.mark.parametrize("phone, result",
                             [("1", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("135123456789", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("0", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("-1", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("135112210.0", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1"*256, {"code": 0, "msg": "手机号码格式不正确"}),
                              ("a", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("中", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("*", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105a", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105中", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105*", {"code": 0, "msg": "手机号码格式不正确"}),
                              (" ", {"code": 0, "msg": "不能为空"}),
                              ("", {"code": 0, "msg": "不能为空"})],
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
                params = {"code_type": 0, "phone": "13511221110", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102013_phone_wrong ({0}) ....".format(phone))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_token值")
    @allure.testcase("FT-HTJK-102-014")
    @pytest.mark.parametrize("code_token, phone, result",
                             [('1' * 256, "13511221059", {"code": 0, "msg": "授权非法"}),
                              ('1.0', "13511221060", {"code": 0, "msg": "授权非法"}),
                              ('a', "13511221061", {"code": 0, "msg": "授权非法"}),
                              ('中', "13511221062", {"code": 0, "msg": "授权非法"}),
                              ('*', "13511221063", {"code": 0, "msg": "授权非法"}),
                              ('1a', "13511221064", {"code": 0, "msg": "授权非法"}),
                              ('1中', "13511221065", {"code": 0, "msg": "授权非法"}),
                              ('1*', "13511221066", {"code": 0, "msg": "授权非法"}),
                              (' ', "13511221067", {"code": 0, "msg": "不能为空"}),
                              ('', "13511221068", {"code": 0, "msg": "不能为空"})],
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                if not code_token1:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102014_codetoken_wrong ({0}) ....".format(code_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误sms_code值")
    @allure.testcase("FT-HTJK-102-015")
    @pytest.mark.parametrize("sms_code, phone, result",
                             [('1' * 256, "13511221069", {"code": 0, "msg": "验证码不正确"}),
                              ('1.0', "13511221070", {"code": 0, "msg": "验证码不正确"}),
                              ('a', "13511221071", {"code": 0, "msg": "验证码不正确"}),
                              ('中', "13511221072", {"code": 0, "msg": "验证码不正确"}),
                              ('*', "13511221073", {"code": 0, "msg": "验证码不正确"}),
                              ('1a', "13511221074", {"code": 0, "msg": "验证码不正确"}),
                              ('1中', "13511221075", {"code": 0, "msg": "验证码不正确"}),
                              ('1*', "13511221076", {"code": 0, "msg": "验证码不正确"}),
                              (' ', "13511221077", {"code": 0, "msg": "不能为空"}),
                              ('', "13511221078", {"code": 0, "msg": "不能为空"})],
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": sms_code, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102015_smscode_wrong ({0}) ....".format(sms_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-102-016")
    @pytest.mark.parametrize("timestamp, phone, result",
                             [(1, "13511221079", {"code": 1, "msg": "登录成功"}),
                              (get_timestamp() + 10000, "13511221080", {"code": 1, "msg": "登录成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": '1.0', "device_token": '123456789',
                        "imei": '46001123456789', "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": timestamp}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result["code"]
                assert result["msg"] in rsp_content["message"]

            with allure.step("teststep5: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                       get_timestamp(), self.logger)
                allure.attach("logout result：", str(logout_result))
                self.logger.info("logout result: {}".format(logout_result))
                self.httpclient.update_header({"authorization": ""})
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102016_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-102-017")
    @pytest.mark.parametrize("timestamp, phone, result",
                             [(1, "13511221081", {"status": 200, "code": 0, "msg": ""}),
                              (9223372036854775807, "13511221082", {"status": 200, "code": 0, "msg": ""}),
                              (0, "13511221083", {"status": 200, "code": 0, "msg": ""}),
                              (-1, "13511221084", {"status": 200, "code": 0, "msg": ""}),
                              (-9223372036854775809, "13511221085", {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, "13511221086", {"status": 400, "code": 0, "msg": ""}),
                              (1.0, "13511221087", {"status": 400, "code": 0, "msg": ""}),
                              ('a', "13511221088", {"status": 400, "code": 0, "msg": ""}),
                              ('中', "13511221089", {"status": 400, "code": 0, "msg": ""}),
                              ('*', "13511221090", {"status": 400, "code": 0, "msg": ""}),
                              ('1a', "13511221091", {"status": 400, "code": 0, "msg": ""}),
                              ('1中', "13511221092", {"status": 400, "code": 0, "msg": ""}),
                              ('1*', "13511221093", {"status": 400, "code": 0, "msg": ""}),
                              (' ', "13511221094", {"status": 400, "code": 0, "msg": ""}),
                              ('', "13511221095", {"status": 400, "code": 0, "msg": ""})],
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": phone, "code_token": code_token,
                        "sms_code": "123456", "timestamp": timestamp}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result["status"]
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content["result"]["user_info"]["member_id"],
                                                   get_timestamp(), self.logger)
                            allure.attach("logout result：", str(logout_result))
                            self.logger.info("logout result: {}".format(logout_result))
                            self.httpclient.update_header({"authorization": ""})
                    assert rsp_content["code"] == result["code"]
                    assert result["msg"] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221096', "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] != 1
                assert len(rsp_content["message"]) > 0
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221097', "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'client_version不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1",
                        "imei": "460011234567890", "phone": '13511221098', "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'device_token不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "phone": '13511221099', "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'imei不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "code_token": code_token,
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221101',
                        "sms_code": "123456", "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221102', "code_token": code_token,
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
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
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "0.1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": '13511221103', "code_token": code_token,
                        "sms_code": "123456"}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep4: assert the response code and content"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '不能为空' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_102025_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Register.py'])
    pytest.main(['-s', 'test_APP_Register.py::TestRegister::test_102001_register_correct'])
