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


@pytest.mark.APP
@allure.feature("APP-获取用户信息")
class TestGetUserInfo(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'UserInfo')
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
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511222001", "sms_code": "123456",
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
        with allure.step("user logout."):
            cls.httpclient.update_header({"authorization": cls.token})
            logout_result = logout(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
            cls.httpclient.update_header({"authorization": None})
            allure.attach("logout result", str(logout_result))
            cls.logger.info("logout result: {0}".format(logout_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("critical")
    @allure.story("正确拉取用户信息")
    @allure.testcase("FT-HTJK-106-001")
    def test_106001_get_userinfo_correct(self):
        """ Test get user info by correct parameters(FT-HTJK-106-001)."""
        self.logger.info(".... Start test_106001_get_userinfo_correct ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
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
                assert '拉取用户信息成功' in rsp_content["message"]
                assert rsp_content["result"]['member_id'] == data['member_id']
                assert rsp_content["result"]['auth_state'] == 0
                assert rsp_content["result"]['feature_state'] == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106001_get_userinfo_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("未登录拉取用户信息")
    @allure.testcase("FT-HTJK-106-002")
    def test_106002_get_userinfo_without_login(self):
        """ Test get user info without login(FT-HTJK-106-002)."""
        self.logger.info(".... Start test_106002_get_userinfo_without_login ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511222102", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_register(self.httpclient, json['client_type'], json['client_version'],
                                       json['device_token'], json['imei'], json['code_type'],
                                        json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                member_id = register_result['user_info']['member_id']
                self.httpclient.update_header({"authorization": register_result['token']})
                logout(self.httpclient, member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})

            with allure.step("teststep2: get parameters."):
                data = {"member_id": member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0},{1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep3: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
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
                assert rsp_content["code"] == 201001
                assert '授权非法' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106002_get_userinfo_without_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-106-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)",  "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_106003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-106-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_106003_token_wrong ({0})....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    self.logger.info("rsp.text: {}".format(rsp.text))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106003_token_wrong ({0})....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-106-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": "is not valid"}),
                              (1.0, {"status": 400,"code": 0, "msg": "is not valid"}),
                              ('中', {"status": 400,"code": 0, "msg": "is not valid"}),
                              ('*', {"status": 400,"code": 0, "msg": "is not valid"}),
                              ('1中', {"status": 400,"code": 0, "msg": "is not valid"}),
                              ('1*', {"status": 400,"code": 0, "msg": "is not valid"}),
                              (' ', {"status": 400,"code": 0, "msg": "is not valid"}),
                              ('', {"status": 400,"code": 0, "msg": "is invalid"})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_106004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-106-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_106004_member_id_wrong ({0})....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                data = {"member_id": member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    rsp_content = rsp.text
                    self.logger.info("response content：{0}".format(rsp_content))
                else:
                    rsp_content = rsp.json()
                assert rsp.status_code == result['status']

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106004_member_id_wrong ({0})....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-106-005")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 1, "msg": ""}), (-1, {"status": 200, "code": 1, "msg": ""}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is not valid"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is not valid"}),
                              (1.0, {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('a', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('中', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('*', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "is not valid"}),
                              (' ', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('', {"status": 400, "code": 0, "msg": "is invalid"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_106005_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-106-005).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_106005_timestamp_wrong ({0})....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                if rsp.status_code != 200:
                    rsp_content = rsp.text
                    self.logger.info("response content：{0}".format(rsp_content))
                else:
                    rsp_content = rsp.json()
                assert rsp.status_code == result['status']

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106005_timestamp_wrong ({0})....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-106-006")
    def test_106006_no_token(self):
        """ Test get user info without token(FT-HTJK-106-006)."""
        self.logger.info(".... Start test_106006_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content['code'] == 201000
                assert '未登录或登录已过期' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106006_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-106-007")
    def test_106007_no_member_id(self):
        """ Test get user info without member_id(FT-HTJK-106-007)."""
        self.logger.info(".... Start test_106007_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                data = {"timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content['code'] == 201001
                assert '授权非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106007_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-106-008")
    def test_106008_no_timestamp(self):
        """ Test get user info without timestamp(FT-HTJK-106-008)."""
        self.logger.info(".... Start test_106008_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content['code'] == 1
                assert '拉取用户信息成功' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_106008_no_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("用户已采集照片")
    @allure.testcase("FT-HTJK-106-009")
    def test_106009_get_userinfo_with_feature(self):
        """ Test get user info with feature(FT-HTJK-106-009)."""
        self.logger.info(".... Start test_106009_get_userinfo_with_feature ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger, "本人")
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                data = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep3: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
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
                assert '拉取用户信息成功' in rsp_content["message"]
                assert rsp_content["result"]['member_id'] == data['member_id']
                assert rsp_content["result"]['auth_state'] == 0
                assert rsp_content["result"]['feature_state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete user identity record"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete user identity record"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_106009_get_userinfo_with_feature ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("用户已认证")
    @allure.testcase("FT-HTJK-106-010")
    def test_106010_get_userinfo_with_authority(self):
        """ Test get user info with authority(FT-HTJK-106-010)."""
        self.logger.info(".... Start test_106010_get_userinfo_with_authority ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                get_timestamp(), self.logger, "本人")
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep3: get parameters."):
                data = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(data, headers))
                self.logger.info("data: {0}, headers: {1}".format(data, headers))

            with allure.step("teststep4: requests http get."):
                rsp = self.httpclient.get(self.URI, params=data, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep5: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep6: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '拉取用户信息成功' in rsp_content["message"]
                assert rsp_content["result"]['member_id'] == data['member_id']
                assert rsp_content["result"]['auth_state'] == 1
                assert rsp_content["result"]['feature_state'] == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("teststep: delete user identity record"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete user identity record"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_106010_get_userinfo_with_authority ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_APP_Get_UserInfo.py'])
    # pytest.main(['-s', 'test_APP_Get_UserInfo.py::TestGetUserInfo::test_106010_get_userinfo_with_authority'])
