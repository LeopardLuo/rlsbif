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


@allure.feature("登录-手机号")
class TestLogin(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'AppLogin')
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
                allure.attach("db_params", "{0}, {1}, {2}, {3}, {4}".format(db_user, db_password, db_host, db_database, db_port))
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
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                cls.logger.info("register params: {0}".format(json))
                register_result = make_register(cls.httpclient, json['client_type'], json['client_version'],
                                       json['device_token'], json['imei'], json['code_type'],
                                        json['phone'], json['sms_code'], json['timestamp'], cls.logger)
                allure.attach("register result", str(register_result))
                cls.logger.info("register result: {0}".format(register_result))
                token = register_result['token']
                member_id = register_result['user_info']['member_id']
                cls.httpclient.update_header({"authorization": token})
                logout_result = logout(cls.httpclient, member_id, get_timestamp(), cls.logger)
                cls.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                cls.logger.info("logout result: {0}".format(logout_result))
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
        with allure.step("delete mem_member_login"):
            table = 'mem_member_login'
            allure.attach("table name and condition", "{0}".format(table))
            self.logger.info("delele records of table: {0}".format(table))
            delete_result = self.mysql.execute_delete_all(table)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("登录成功")
    @allure.testcase("FT-HTJK-103-001")
    def test_103001_login_correct(self):
        """ Test login by correct parameters(FT-HTJK-103-001)."""
        self.logger.info(".... Start test_103001_login_correct ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()-10}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '登录成功' in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                assert select_result[0][1] == json['phone']
                assert select_result[0][3] == json['device_token']
                assert select_result[0][6] == json['imei']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103001_login_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("重复登录")
    @allure.testcase("FT-HTJK-103-002")
    def test_103002_repeat_login(self):
        """ Test repeat login twice(FT-HTJK-103-002)."""
        self.logger.info(".... Start test_103002_repeat_login ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post login first time."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '登录成功' in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: requests http post login second time."):
                rsp2 = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp2.request.headers))
                allure.attach("request.body", str(rsp2.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp2.request.headers))
                self.logger.info("request.body: {}".format(rsp2.request.body.decode()))

            with allure.step("teststep7: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp2.status_code))
                self.logger.info("Actual response code：{0}".format(rsp2.status_code))
                assert rsp2.status_code == 200
                rsp2_content = rsp2.json()

            with allure.step("teststep8: assert the response content"):
                allure.attach("response content：", str(rsp2_content))
                self.logger.info("response content: {}".format(rsp2_content))
                assert rsp2_content["code"] == 0
                assert '用户登录异常' in rsp2_content["message"]

            with allure.step("teststep9: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{0}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103002_repeat_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_type值")
    @allure.testcase("FT-HTJK-103-003")
    @pytest.mark.parametrize("client_type, result",
                             [(1, {"code": 1, "msg": ""}), (2, {"code": 1, "msg": ""}),
                              (3, {"code": 1, "msg": ""}), (4, {"code": 1, "msg": ""})],
                             ids=["client_type(0)", "client_type(1)", "client_type(2)", "client_type(3)"])
    def test_103003_clienttype_correct(self, client_type, result):
        """ Test correct client_type values (0, 1, 2, 3) (FT-HTJK-103-003).
        :param client_type: client_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103003_clienttype_correct ({0}) ....".format(client_type))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '登录成功' in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103003_clienttype_correct ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_type值")
    @allure.testcase("FT-HTJK-103-004")
    @pytest.mark.parametrize("client_type, result",
                             [(-1, {"status": 200, "msg": "client_type值非法", "code": 0}), (5, {"status": 200, "msg": "client_type值非法", "code": 0}),
                              (-2147483649, {"status": 400, "msg": "", "code": 0}), (2147483648, {"status": 400, "msg": "", "code": 0}),
                              (1.0, {"status": 400, "msg": "", "code": 0}), ('a', {"status": 400, "msg": "", "code": 0}),
                              ('中', {"status": 400, "msg": "", "code": 0}), ('*', {"status": 400, "msg": "", "code": 0}),
                              ('1a', {"status": 400, "msg": "", "code": 0}), ('1中', {"status": 400, "msg": "", "code": 0}),
                              ('1*', {"status": 400, "msg": "", "code": 0}), (' ', {"status": 400, "msg": "", "code": 0}),
                              ('', {"status": 400, "msg": "", "code": 0})],
                             ids=["client_type(-1)", "client_type(4)", "client_type(超小值)", "client_type(超大值)",
                                  "client_type(小数)", "client_type(字母)", "client_type(中文)",
                                  "client_type(特殊字符)", "client_type(数字字母)", "client_type(数字中文)",
                                  "client_type(数字特殊字符)", "client_type(空格)", "client_type(空)"])
    def test_103004_clienttype_wrong(self, client_type, result):
        """ Test wrong client_type values (-1、4、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-004).
        :param client_type: client_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103004_clienttype_wrong ({0}) ....".format(client_type))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": client_type, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", str(result['status']))
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] == 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103004_clienttype_wrong ({0}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确client_version值")
    @allure.testcase("FT-HTJK-103-005")
    @pytest.mark.parametrize("client_version, result",
                             [('a' * 50, {"code": 1, "msg": "登录成功"}),(1.0, {"code": 1, "msg": "登录成功"}),
                             ('a', {"code": 1, "msg": "登录成功"}), ('中', {"code": 1, "msg": "登录成功"}),
                             ('*', {"code": 1, "msg": "登录成功"}), ('1a', {"code": 1, "msg": "登录成功"}),
                             ('1中', {"code": 1, "msg": "登录成功"}), ('1*', {"code": 1, "msg": "登录成功"}),],
                             ids=["client_version(最大长度值)", "client_version(小数)", "client_version(字母)",
                                  "client_version(中文)", "client_version(特殊字符)", "client_version(数字字母)",
                                  "client_version(数字中文)", "client_version(数字特殊字符)",])
    def test_103005_clientversion_correct(self, client_version, result):
        """ Test correct client_version values (最大长度值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符) (FT-HTJK-103-005).
        :param client_version: client_version parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103005_clientversion_correct ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103005_clientversion_correct ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_version值")
    @allure.testcase("FT-HTJK-103-006")
    @pytest.mark.parametrize("client_version, result",
                             [('1' * 1001, {"msg": "", "code": 0}),
                              (' ', {"msg": "client_version不能为空", "code": 0}), ('', {"msg": "client_version不能为空", "code": 0})],
                             ids=["client_version(超长值)",  "client_version(空格)", "client_version(空)"])
    def test_103006_clientversion_wrong(self, client_version, result):
        """ Test wrong client_type values (超长值、空格、空）(FT-HTJK-103-006).
        :param client_version: client_version parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103006_clientversion_wrong ({0}) ....".format(client_version))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103006_clientversion_wrong ({0}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确device_token值")
    @allure.testcase("FT-HTJK-103-007")
    @pytest.mark.parametrize("device_token, result",
                             [('1', {"code": 1, "msg": "登录成功"}), ('a' * 50, {"code": 1, "msg": "登录成功"}),
                              (1.0, {"code": 1, "msg": "登录成功"}),
                              ('a', {"code": 1, "msg": "登录成功"}), ('中', {"code": 1, "msg": "登录成功"}),
                              ('*', {"code": 1, "msg": "登录成功"}), ('1a', {"code": 1, "msg": "登录成功"}),
                              ('1中', {"code": 1, "msg": "登录成功"}), ('1*', {"code": 1, "msg": "登录成功"}),
                              ],
                             ids=["device_token(最小长度值)", "device_token(最大长度值)","device_token(小数)",
                                  "device_token(字母)", "device_token(中文)",
                                  "device_token(特殊字符)", "device_token(数字字母)", "device_token(数字中文)",
                                  "device_token(数字特殊字符)", ])
    def test_103007_devicetoken_correct(self, device_token, result):
        """ Test correct device_token values (最小长度值、最大长度值) (FT-HTJK-103-007).
        :param device_token: device_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103007_devicetoken_correct ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": device_token,
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103007_devicetoken_correct ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误device_token值")
    @allure.testcase("FT-HTJK-103-008")
    @pytest.mark.parametrize("device_token, result",
                             [('1' * 1001, {"code": 0, "msg": ""}),
                              (' ', {"code": 0, "msg": "不能为空"}), ('', {"code": 0, "msg": "不能为空"})],
                             ids=["device_token(超长值)", "device_token(空格)", "device_token(空)"])
    def test_103008_devicetoken_wrong(self, device_token, result):
        """ Test wrong device_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-008).
        :param device_token: device_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103008_devicetoken_wrong ({0}) ....".format(device_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": device_token,
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103008_devicetoken_wrong ({0}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确imei值")
    @allure.testcase("FT-HTJK-103-009")
    @pytest.mark.parametrize("imei, result",
                             [('460011234567890', {"code": 1, "msg": "登录成功"}),
                              ('46001123456789012', {"code": 1, "msg": "登录成功"})],
                             ids=["imei(最小长度值)", "imei(最大长度值)"])
    def test_103009_imei_correct(self, imei, result):
        """ Test correct imei values (最小长度值、最大长度值) (FT-HTJK-103-009).
        :param imei: imei parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103009_imei_correct ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '460011234567890',
                        "imei": imei, "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                       get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103009_imei_correct ({0}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误imei值")
    @allure.testcase("FT-HTJK-103-010")
    @pytest.mark.parametrize("imei, result",
                             [('1' * 18, {"code": 0, "msg": "长度"}), (12345678901234.0, {"code": 0, "msg": ""}),
                              ('a'*15, {"code": 0, "msg": ""}), ('中'*15, {"code": 0, "msg": ""}),
                              ('*'*15, {"code": 0, "msg": ""}), ('1a'*8, {"code": 0, "msg": ""}),
                              ('1中'*8, {"code": 0, "msg": ""}), ('1*'*8, {"code": 0, "msg": ""}),
                              (' '*15, {"code": 0, "msg": "长度"}), ('', {"code": 0, "msg": "长度"})],
                             ids=["imei(超长值)", "imei(小数)", "imei(字母)", "imei(中文)",
                                  "imei(特殊字符)", "imei(数字字母)", "imei(数字中文)",
                                  "imei(数字特殊字符)", "imei(空格)", "imei(空)"])
    def test_103010_imei_wrong(self, imei, result):
        """ Test wrong imei values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-010).
        :param imei: imei parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103010_imei_wrong ({0}) ....".format(imei))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '123456789',
                        "imei": imei, "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103010_imei_wrong ({0}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号未注册未获取验证码")
    @allure.testcase("FT-HTJK-103-011")
    def test_103011_not_register_not_getmsgcode(self):
        """ Test login not register not get msg code(FT-HTJK-103-011)."""
        self.logger.info(".... Start test_103011_not_register_not_getmsgcode ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
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
                        "imei": "460011234567890", "phone": "13511222002", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103011_not_register_not_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号未注册获取验证码")
    @allure.testcase("FT-HTJK-103-012")
    def test_103012_not_register_getmsgcode(self):
        """ Test login not register get msg code(FT-HTJK-103-012)."""
        self.logger.info(".... Start test_103012_not_register_getmsgcode ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222002", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222002", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert rsp_content["Message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103012_not_register_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("手机号已注册未获取验证码")
    @allure.testcase("FT-HTJK-103-013")
    def test_103013_register_not_getmsgcode(self):
        """ Test login register not get msg code(FT-HTJK-103-013)."""
        self.logger.info(".... Start test_103013_register_not_getmsgcode ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222002", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103013_register_not_getmsgcode ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-103-014")
    @pytest.mark.parametrize("phone, result",
                             [("1", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("135123456789", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("0", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("-1", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("135112210.0", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1" * 256, {"code": 0, "msg": "手机号码格式不正确"}),
                              ("a", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("中", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("*", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105a", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105中", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("1351122105*", {"code": 0, "msg": "手机号码格式不正确"}),
                              (" ", {"code": 0, "msg": "手机号码格式不正确"}),
                              ("", {"code": 0, "msg": "手机号码格式不正确"})],
                             ids=["phone(1)", "phone(12位)", "phone(0)", "phone(-1)", "phone(小数)", "phone(超长值)",
                                  "phone(字母)", "phone(中文)", "phone(特殊字符)", "phone(数字字母)", "phone(数字中文)",
                                  "phone(数字特殊字符)", "phone(空格)", "phone(空)"])
    def test_103014_phone_wrong(self, phone, result):
        """ Test wrong phone values (1、12位、0、-1、小数、超长值、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-014).
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103014_phone_wrong ({0}) ....".format(phone))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '123456789',
                        "imei": '460011234567890', "phone": phone, "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103014_phone_wrong ({0}) ....".format(phone))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误sms_code值")
    @allure.testcase("FT-HTJK-103-015")
    @pytest.mark.parametrize("sms_code, result",
                             [('1' * 256, {"code": 0, "msg": "验证码不正确"}), (1.0, {"code": 0, "msg": "验证码不正确"}),
                              ('a', {"code": 0, "msg": "验证码不正确"}), ('中', {"code": 0, "msg": "验证码不正确"}),
                              ('*', {"code": 0, "msg": "验证码不正确"}), ('1a', {"code": 0, "msg": "验证码不正确"}),
                              ('1中', {"code": 0, "msg": "验证码不正确"}), ('1*', {"code": 0, "msg": "验证码不正确"}),
                              (' ', {"code": 0, "msg": "验证码不正确"}), ('', {"code": 0, "msg": "验证码不正确"})],
                             ids=["sms_code(超长值)", "sms_code(小数)", "sms_code(字母)", "sms_code(中文)",
                                  "sms_code(特殊字符)", "sms_code(数字字母)", "sms_code(数字中文)",
                                  "sms_code(数字特殊字符)", "sms_code(空格)", "sms_code(空)"])
    def test_103015_smscode_wrong(self, sms_code, result):
        """ Test wrong sms_code values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-015).
        :param sms_code: sms_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103015_smscode_wrong ({0}) ....".format(sms_code))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '123456789',
                        "imei": '460011234567890', "phone": "13511222001", "sms_code": sms_code,
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103015_smscode_wrong ({0}) ....".format(sms_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_token值")
    @allure.testcase("FT-HTJK-103-016")
    @pytest.mark.parametrize("code_token, result",
                             [('1' * 256, {"code": 0, "msg": "授权非法"}), ('1.0', {"code": 0, "msg": "授权非法"}),
                              ('a', {"code": 0, "msg": "授权非法"}), ('中', {"code": 0, "msg": "授权非法"}),
                              ('*', {"code": 0, "msg": "授权非法"}), ('1a', {"code": 0, "msg": "授权非法"}),
                              ('1中', {"code": 0, "msg": "授权非法"}), ('1*', {"code": 0, "msg": "授权非法"}),
                              (' ', {"code": 0, "msg": "不能为空"}), ('', {"code": 0, "msg": "不能为空"})],
                             ids=["code_token(超长值)", "code_token(小数)", "code_token(字母)", "code_token(中文)",
                                  "code_token(特殊字符)", "code_token(数字字母)", "code_token(数字中文)",
                                  "code_token(数字特殊字符)", "code_token(空格)", "code_token(空)"])
    def test_103016_codetoken_wrong(self, code_token, result):
        """ Test wrong code_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-016).
        :param code_token: code_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103016_codetoken_wrong ({0}) ....".format(code_token))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                if not code_token1:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '123456789',
                        "imei": '460011234567890', "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103016_codetoken_wrong ({0}) ....".format(code_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-103-017")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"code": 1, "msg": "登录成功"}), (get_timestamp() + 100, {"code": 1, "msg": "登录成功"})],
                             ids=["timestamp(最小长度值)", "timestamp(最大长度值)"])
    def test_103017_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值) (FT-HTJK-103-017).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103017_timestamp_correct ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '460011234567890',
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": timestamp}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
                assert rsp_content["result"]["token"]

            with allure.step("teststep6: user logout"):
                self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'], get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("Logout result：", str(logout_result))
                self.logger.info("Logout result：{0}".format(logout_result))

            with allure.step("teststep7: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103017_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-103-018")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 0, "msg": ""}), (9223372036854775807, {"status": 200, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": ""}), (-1, {"status": 200, "code": 0, "msg": ""}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}), ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}), ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}), ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}), (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_103018_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-018).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_103018_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": '123456789',
                        "imei": '460011234567890', "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": timestamp}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103018_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_type参数")
    @allure.testcase("FT-HTJK-103-019")
    def test_103019_no_clienttype(self):
        """ Test login without client_type(FT-HTJK-103-019)."""
        self.logger.info(".... Start test_103019_no_clienttype ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
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
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'client_type值非法' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103019_no_clienttype ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_version参数")
    @allure.testcase("FT-HTJK-103-020")
    def test_103020_no_client_version(self):
        """ Test login without client_version(FT-HTJK-103-020)."""
        self.logger.info(".... Start test_103020_no_client_version ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
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
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'client_version' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103020_no_client_version ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_token参数")
    @allure.testcase("FT-HTJK-103-021")
    def test_103021_no_device_token(self):
        """ Test login without device_token(FT-HTJK-103-021)."""
        self.logger.info(".... Start test_103021_no_device_token ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
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
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'device_token' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103021_no_device_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少imei参数")
    @allure.testcase("FT-HTJK-103-022")
    def test_103022_no_imei(self):
        """ Test login without imei(FT-HTJK-103-022)."""
        self.logger.info(".... Start test_103022_no_imei ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
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
                        "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'imei' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103022_no_imei ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少phone参数")
    @allure.testcase("FT-HTJK-103-023")
    def test_103023_no_phone(self):
        """ Test login without phone(FT-HTJK-103-023)."""
        self.logger.info(".... Start test_103023_no_phone ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "sms_code": "123456",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'phone' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103023_no_phone ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少sms_code参数")
    @allure.testcase("FT-HTJK-103-024")
    def test_103024_no_sms_code(self):
        """ Test login without sms_code(FT-HTJK-103-024)."""
        self.logger.info(".... Start test_103024_no_sms_code ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222001",
                        "code_token": code_token, "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert '验证码不正确' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103024_no_sms_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少code_token参数")
    @allure.testcase("FT-HTJK-103-025")
    def test_103025_no_code_token(self):
        """ Test login without code_token(FT-HTJK-103-025)."""
        self.logger.info(".... Start test_103025_no_code_token ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'code_token' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103025_no_code_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-103-026")
    def test_103026_no_timestamp(self):
        """ Test login without timestamp(FT-HTJK-103-026)."""
        self.logger.info(".... Start test_103026_no_timestamp ....")
        try:
            with allure.step("teststep1: get msg code."):
                params = {"code_type": 2, "phone": "13511222001", "timestamp": get_timestamp()}
                allure.attach("getmsgcode params value", str(params))
                self.logger.info("getmsgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                if not code_token:
                    assert False

            with allure.step("teststep2: get parameters."):
                json = {"client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
                        "code_token": code_token}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
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
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": rsp_content["result"]["token"]})
                            logout_result = logout(self.httpclient, rsp_content['result']['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == 0
                assert 'timestamp' in rsp_content["message"]

            with allure.step("teststep6: query database records"):
                table = 'mem_member_login'
                allure.attach("table name and condition", "{0}".format(table))
                self.logger.info("")
                self.logger.info("table: {0}".format(table))
                select_result = self.mysql.execute_select_all(table)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_103026_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Login.py'])
    pytest.main(['-s', 'test_APP_Login.py::TestLogin::test_103003_clienttype_correct'])
