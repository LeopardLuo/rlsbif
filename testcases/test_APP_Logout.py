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


@allure.feature("APP-退出登录")
class TestLogout(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'Logout')
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
                allure.attach("db_params", "{0},{1},{2},{3},{4}".format(db_user, db_password, db_host, db_database, db_port))
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
                        "imei": "460011234567890", "phone": "13511223001", "sms_code": "123456",
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
        with allure.step("user login."):
            json = {"code_type": 2, "client_type": 1, "client_version": "v1", "device_token": "460011234567890",
                    "imei": "460011234567890", "phone": "13511223001", "sms_code": "123456", "timestamp": get_timestamp()}
            allure.attach("login params value", str(json))
            self.logger.info("login params: {0}".format(json))
            self.login_result = make_login(self.httpclient, json['code_type'], json['client_type'], json['client_version'],
                                      json['device_token'], json['imei'], json['phone'], json['sms_code'],
                                      json['timestamp'],
                                      self.logger)
            allure.attach("login result", str(self.login_result))
            self.logger.info("login result: {0}".format(self.login_result))
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
    @allure.story("退出成功")
    @allure.testcase("FT-HTJK-105-001")
    def test_105001_logout_correct(self):
        """ Test logout by correct parameters(FT-HTJK-105-001)."""
        self.logger.info(".... Start test_105001_logout_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization":token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                self.httpclient.update_header({"authorization": None})
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

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
                assert '退出成功' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105001_logout_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("重复退出")
    @allure.testcase("FT-HTJK-105-002")
    def test_105002_repeat_logout(self):
        """ Test repeat logout (FT-HTJK-105-002)."""
        self.logger.info(".... Start test_105002_repeat_logout ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout first time."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '退出成功' in rsp_content["message"]

            with allure.step("teststep5: requests http logout second time."):
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                self.httpclient.update_header({"authorization": None})
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep6: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep7: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105002_repeat_logout ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-105-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 101, {"code": 0, "msg": ""}), ('1.0', {"code": 0, "msg": ""}),
                              ('中', {"code": 0, "msg": ""}), ('*', {"code": 0, "msg": ""}),
                              ('1中', {"code": 0, "msg": ""}), ('1*', {"code": 0, "msg": ""}),
                              (' ', {"code": 0, "msg": ""}), ('', {"code": 0, "msg": ""})],
                             ids=["token(超长值)", "token(小数)", "token(中文)",
                                  "token(特殊字符)", "token(数字中文)",
                                  "token(数字特殊字符)", "token(空格)", "token(空)"])
    def test_105003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-105-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_105003_token_wrong ({0}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, json['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp_content["code"] != 1:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, json['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.httpclient.update_header({"authorization": None})
            self.logger.info(".... End test_105003_token_wrong ({0}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("用户未登录，token空")
    @allure.testcase("FT-HTJK-105-004")
    def test_105004_not_login_token_empty(self):
        """ Test logout with token empty(FT-HTJK-105-004)."""
        self.logger.info(".... Start test_105004_not_login_token_empty ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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
                rsp_content = rsp.json()

            with allure.step("teststep4: logout with token empty"):
                self.httpclient.update_header({"token": ""})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep5: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep6: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.httpclient.update_header({"authorization": None})
            self.logger.info(".... End test_105004_not_login_token_empty ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-105-005")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"code": 0, "msg": ""}), (1.0, {"code": 0, "msg": ""}),
                              ('中', {"code": 0, "msg": ""}), ('*', {"code": 0, "msg": ""}),
                              ('1中', {"code": 0, "msg": ""}), ('1*', {"code": 0, "msg": ""}),
                              (' ', {"code": 0, "msg": ""}), ('', {"code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_105005_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-105-005).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_105005_member_id_wrong ({0}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] != 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": self.login_result['token']})
                            logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.httpclient.update_header({"authorization": None})
            self.logger.info(".... End test_105005_member_id_wrong ({0}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-105-006")
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
    def test_105006_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-103-018).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_105006_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": timestamp}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] != 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": self.login_result['token']})
                            logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.httpclient.update_header({"authorization": None})
            self.logger.info(".... End test_105006_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-105-007")
    def test_105007_no_token(self):
        """ Test logout without token(FT-HTJK-105-007)."""
        self.logger.info(".... Start test_105007_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                self.httpclient.update_header({"authorization": None})
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] != 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": self.login_result['token']})
                            logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == 0
                    assert '' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105007_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-105-008")
    def test_105008_no_member_id(self):
        """ Test logout without member_id(FT-HTJK-105-008)."""
        self.logger.info(".... Start test_105008_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"timestamp": get_timestamp()}
                self.httpclient.update_header({"authorization": token})
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] != 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": self.login_result['token']})
                            logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == 0
                    assert '' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105008_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-105-009")
    def test_105009_no_timestamp(self):
        """ Test logout without timestamp(FT-HTJK-105-009)."""
        self.logger.info(".... Start test_105009_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                if not self.login_result:
                    assert False
                token = self.login_result['token']
                member_id = self.login_result['user_info']['member_id']
                allure.attach("token value", str(token))
                allure.attach("member_id value", str(member_id))
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"member_id": member_id}
                self.httpclient.update_header({"authorization": token})
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body.decode()))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    with allure.step("user logout"):
                        self.httpclient.update_header({"authorization": self.login_result['token']})
                        logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                               get_timestamp(), self.logger)
                        self.httpclient.update_header({"authorization": None})
                        allure.attach("Logout result：", str(logout_result))
                        self.logger.info("Logout result：{0}".format(logout_result))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if rsp_content["code"] != 1:
                        with allure.step("user logout"):
                            self.httpclient.update_header({"authorization": self.login_result['token']})
                            logout_result = logout(self.httpclient, self.login_result['user_info']['member_id'],
                                                   get_timestamp(), self.logger)
                            self.httpclient.update_header({"authorization": None})
                            allure.attach("Logout result：", str(logout_result))
                            self.logger.info("Logout result：{0}".format(logout_result))
                    assert rsp_content["code"] == 0
                    assert '' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105009_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Logout.py'])
    pytest.main(['-s', 'test_APP_Logout.py::TestLogout::test_105001_logout_correct'])
