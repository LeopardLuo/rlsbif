#!/usr/bin/env python3
# -*-coding:utf-8-*-

import datetime
import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *


@pytest.mark.H5
@allure.feature("H5-登录")
class TestHomeIndex(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'H5HomeIndex')
                allure.attach("uri", str(cls.URI))
                cls.logger.info("uri: " + cls.URI)
            with allure.step("初始化HTTP客户端。"):
                cls.sv_protocol = cls.config.getItem('server', 'protocol')
                cls.sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(cls.sv_protocol, cls.sv_host, sv_port)
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
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("critical")
    @allure.story("登录成功")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_home_index_correct(self):
        """ Test home index with correct parameters. """
        self.logger.info(".... Start test_home_index_correct ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                                json['device_token'], json['imei'], json['code_type'],
                                                json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"token": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("登录"):
                    with allure.step("teststep: get parameters."):
                        data = {"userId": self.member_id, "token": self.token}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.get(uri=self.URI, params=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.text
                        rsp_headers = rsp.headers
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        allure.attach("response headers：", str(rsp_headers))
                        self.logger.info("response headers: {}".format(rsp_headers))
                        assert rsp_content
                        assert rsp_headers['Set-Cookie']

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_home_index_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误userId值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("userId, result",
                             [('1' * 256, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (1.5, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('*', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('%1%', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (' ', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (11111, {"status": 200, "code": '301', "msg": "该服务商已停止服务"}),
                              (0, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (-1, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["userId(超长值)", "userId(小数)", "userId(英文)", "userId(中文)",
                                  "userId(特殊字符)", "userId(数字英文)", "userId(数字中文)",
                                  "userId(数字特殊字符)", "userId(空格)", "userId(空)",
                                  "userId(1)", "userId(0)", "userId(-1)", "userId(超大)",
                                  "userId(超小)"])
    def test_home_index_userid_wrong(self, userId, result):
        """ Test wrong userId values (FT-HTJK-xxx-xxx).
        :param userId: userId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_home_index_userid_wrong ({}) ....".format(userId))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                                json['device_token'], json['imei'], json['code_type'],
                                                json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"token": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("登录"):
                    with allure.step("teststep: get parameters."):
                        data = {"userId": userId, "token": self.token}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.get(uri=self.URI, params=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.text
                        rsp_headers = rsp.headers
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        allure.attach("response headers：", str(rsp_headers))
                        self.logger.info("response headers: {}".format(rsp_headers))
                        assert rsp_content
                        assert 'Set-Cookie' not in rsp_headers

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_home_index_userid_wrong ({}) ....".format(userId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (1.5, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('*', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('%1%', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (' ', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (11111, {"status": 200, "code": '301', "msg": "该服务商已停止服务"}),
                              (0, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (-1, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["token(超长值)", "token(小数)", "token(英文)", "token(中文)",
                                  "token(特殊字符)", "token(数字英文)", "token(数字中文)",
                                  "token(数字特殊字符)", "token(空格)", "token(空)",
                                  "token(1)", "token(0)", "token(-1)", "token(超大)",
                                  "token(超小)"])
    def test_home_index_token_wrong(self, token, result):
        """ Test wrong token values (FT-HTJK-xxx-xxx).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_home_index_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                                json['device_token'], json['imei'], json['code_type'],
                                                json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"token": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("登录"):
                    with allure.step("teststep: get parameters."):
                        data = {"userId": self.member_id, "token": token}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.get(uri=self.URI, params=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.text
                        rsp_headers = rsp.headers
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        allure.attach("response headers：", str(rsp_headers))
                        self.logger.info("response headers: {}".format(rsp_headers))
                        assert rsp_content
                        assert 'Set-Cookie' not in rsp_headers

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_home_index_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少userId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_home_index_without_userid(self):
        """ Test home index without userId parameters. """
        self.logger.info(".... Start test_home_index_without_userid ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                                json['device_token'], json['imei'], json['code_type'],
                                                json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"token": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("登录"):
                    with allure.step("teststep: get parameters."):
                        data = {"token": self.token}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.get(uri=self.URI, params=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.text
                        rsp_headers = rsp.headers
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        allure.attach("response headers：", str(rsp_headers))
                        self.logger.info("response headers: {}".format(rsp_headers))
                        assert rsp_content
                        assert 'Set-Cookie' not in rsp_headers.keys()

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_home_index_without_userid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_home_index_without_token(self):
        """ Test home index without token parameters. """
        self.logger.info(".... Start test_home_index_without_token ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                                json['device_token'], json['imei'], json['code_type'],
                                                json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"token": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("登录"):
                    with allure.step("teststep: get parameters."):
                        data = {"userId": self.member_id}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.get(uri=self.URI, params=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.text
                        rsp_headers = rsp.headers
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        allure.attach("response headers：", str(rsp_headers))
                        self.logger.info("response headers: {}".format(rsp_headers))
                        assert rsp_content
                        assert 'Set-Cookie' not in rsp_headers.keys()

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_home_index_without_token ....")
            self.logger.info("")


if __name__ == "__main__":
    # pytest.main(['-s', 'test_H5_Home_Index.py'])
    pytest.main(['-s', 'test_H5_Home_Index.py::TestHomeIndex::test_home_index_userid_wrong'])
