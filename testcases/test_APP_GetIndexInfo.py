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
@allure.feature("APP-获取首页信息")
class TestGetIndexInfo(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'GetIndexInfo')
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
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511222333", "sms_code": "123456",
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
    @allure.story("正确拉取主页信息")
    @allure.testcase("FT-HTJK-127-001")
    def test_127001_get_indexinfo_correct(self):
        """ Test get index info by correct parameters(FT-HTJK-127-001)."""
        self.logger.info(".... Start test_127001_get_indexinfo_correct ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 999, "latitude": 999, "timestamp": get_timestamp()}
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
                assert not rsp_content["message"]
                assert rsp_content["result"]['data']['category']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127001_get_indexinfo_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("未登录拉取主页信息")
    @allure.testcase("FT-HTJK-127-002")
    def test_127002_get_indexinfo_without_login(self):
        """ Test get index info without login(FT-HTJK-127-002)."""
        self.logger.info(".... Start test_127002_get_indexinfo_without_login ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511222302", "sms_code": "123456",
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
                data = {"member_id": member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                assert '授权与当前登录用户不符' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127002_get_indexinfo_without_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-127-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 101000, "msg": "参数错误"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_127003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127003_token_wrong ({}) ....".format(token))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
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
            self.logger.info(".... End Start test_127003_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-127-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_127004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127004_member_id_wrong ({}) ....".format(member_id))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127004_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确category值")
    @allure.testcase("FT-HTJK-127-005")
    @pytest.mark.parametrize("category, result",
                             [(0, {"code": 1, "msg": ""}),
                              (1, {"code": 1, "msg": ""}),
                              (2, {"code": 1, "msg": ""}),
                              (2147483647, {"code": 1, "msg": ""}),],
                             ids=["category(0)", "category(1)", "category(2)", "category(2147483647)"])
    def test_127005_category_correct(self, category, result):
        """ Test correct category values (0、1）(FT-HTJK-127-005).
        :param category: category parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127005_category_correct ({}) ....".format(category))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": category, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127005_category_correct ({}) ....".format(category))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误category值")
    @allure.testcase("FT-HTJK-127-006")
    @pytest.mark.parametrize("category, result",
                             [(-1, {"status": 200, "code": 101000, "msg": "category值非法"}),
                              (-2147483649, {"status": 400, "code": 0, "msg": ""}),
                              (1.5, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (2147483648, {"status": 400, "code": 0, "msg": ""})],
                             ids=["category(-1)", "category( 超小)", "category(小数)", "category(中文)",
                                  "category(特殊字符)", "category(数字中文)",
                                  "category(数字特殊字符)", "category(空格)", "category(空)","category(超大)"])
    def test_127006_category_wrong(self, category, result):
        """ Test wrong category values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-006).
        :param category: category parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127006_category_wrong ({}) ....".format(category))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": category, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127006_category_wrong ({}) ....".format(category))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确longitude值")
    @allure.testcase("FT-HTJK-127-007")
    @pytest.mark.parametrize("longitude, result",
                             [(-180, {"code": 1, "msg": ""}), (-100.5, {"code": 1, "msg": ""}),
                              (0, {"code": 1, "msg": ""}), (1, {"code": 1, "msg": ""}),
                              (100.5, {"code": 1, "msg": ""}), (180, {"code": 1, "msg": ""}),
                              (-1, {"code": 1, "msg": ""})],
                             ids=["longitude(-180)", "longitude(-100.5)", "longitude(0)", "longitude(1)",
                                  "longitude(100.5)", "longitude(180)", "longitude(-1)"])
    def test_127007_longitude_correct(self, longitude, result):
        """ Test correct longitude values (-180、-100.5、0、1、100.5、180、999）(FT-HTJK-127-007).
        :param longitude: longitude parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127007_longitude_correct ({}) ....".format(longitude))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": longitude, "latitude": 10,
                        "timestamp": get_timestamp()}
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127007_longitude_correct ({}) ....".format(longitude))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误longitude值")
    @allure.testcase("FT-HTJK-127-008")
    @pytest.mark.parametrize("longitude, result",
                             [(-181, {"status": 200, "code": 101000, "msg": "longitude值非法"}),
                              (181, {"status": 200, "code": 101000, "msg": "longitude值非法"}),
                              (1000, {"status": 200, "code": 101000, "msg": "longitude值非法"}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["longitude(-181)", "longitude( 181)", "longitude(1000)", "longitude(字母)",
                                  "longitude(中文)", "longitude(特殊字符)", "longitude(数字字母)","longitude(数字中文)",
                                  "longitude(数字特殊字符)", "longitude(空格)", "longitude(空)"])
    def test_127008_longitude_wrong(self, longitude, result):
        """ Test wrong longitude values (超长值、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-008).
        :param longitude: longitude parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127008_longitude_wrong ({}) ....".format(longitude))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": longitude, "latitude": 10,
                        "timestamp": get_timestamp()}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127008_longitude_wrong ({}) ....".format(longitude))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确latitude值")
    @allure.testcase("FT-HTJK-127-009")
    @pytest.mark.parametrize("latitude, result",
                             [(-90, {"code": 1, "msg": ""}), (-10.5, {"code": 1, "msg": ""}),
                              (0, {"code": 1, "msg": ""}), (1, {"code": 1, "msg": ""}),
                              (10.5, {"code": 1, "msg": ""}), (90, {"code": 1, "msg": ""}),
                              (-1, {"code": 1, "msg": ""})],
                             ids=["latitude(-90)", "latitude(-10.5)", "latitude(0)", "latitude(1)",
                                  "latitude(10.5)", "latitude(90)", "latitude(-1)"])
    def test_127009_latitude_correct(self, latitude, result):
        """ Test correct latitude values (-90、-10.5、0、1、10.5、90、999）(FT-HTJK-127-009).
        :param latitude: latitude parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127009_latitude_correct ({}) ....".format(latitude))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 10, "latitude": latitude,
                        "timestamp": get_timestamp()}
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127009_latitude_correct ({}) ....".format(latitude))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误latitude值")
    @allure.testcase("FT-HTJK-127-010")
    @pytest.mark.parametrize("latitude, result",
                             [(-91, {"status": 200, "code": 101000, "msg": "latitude值非法"}),
                              (91, {"status": 200, "code": 101000, "msg": "latitude值非法"}),
                              (1000, {"status": 200, "code": 101000, "msg": "latitude值非法"}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["latitude(-91)", "latitude( 91)", "latitude(1000)", "latitude(字母)",
                                  "latitude(中文)", "latitude(特殊字符)", "latitude(数字字母)", "latitude(数字中文)",
                                  "latitude(数字特殊字符)", "latitude(空格)", "latitude(空)"])
    def test_127010_latitude_wrong(self, latitude, result):
        """ Test wrong latitude values (超长值、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-010).
        :param latitude: latitude parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127010_latitude_wrong ({}) ....".format(latitude))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 10, "latitude": latitude,
                        "timestamp": get_timestamp()}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127010_latitude_wrong ({}) ....".format(latitude))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-127-011")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": ""}),
                              (get_timestamp() + 300, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_127011_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-127-011).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127011_timestamp_correct ({}) ....".format(timestamp))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": timestamp}
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127011_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-114-005")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 101000, "msg": "timestamp值已过期"}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "timestamp值已过期"}),
                              (-1, {"status": 200, "code": 101000, "msg": "timestamp值已过期"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_127012_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-127-012).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_127012_timestamp_wrong ({}) ....".format(timestamp))
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": timestamp}
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
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127012_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-127-013")
    def test_127013_no_token(self):
        """ Test get index info without token(FT-HTJK-127-013)."""
        self.logger.info(".... Start test_127013_no_token ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 101000
                assert '参数错误，请附带授权信息' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127013_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-127-014")
    def test_127014_no_member_id(self):
        """ Test get index info without member_id(FT-HTJK-127-014)."""
        self.logger.info(".... Start test_127014_no_member_id ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"category": 0, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                assert rsp_content["code"] == 101000
                assert '参数错误' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127014_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少category参数")
    @allure.testcase("FT-HTJK-127-015")
    def test_127015_no_category(self):
        """ Test get index info without category(FT-HTJK-127-015)."""
        self.logger.info(".... Start test_127015_no_category ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "longitude": 999, "latitude": 999,
                        "timestamp": get_timestamp()}
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
                assert rsp_content["result"]['data']['category'] == [1, 2, 3, 5, 7]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127015_no_category ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少longitude参数")
    @allure.testcase("FT-HTJK-127-016")
    def test_127016_no_longitude(self):
        """ Test get index info without longitude(FT-HTJK-127-016)."""
        self.logger.info(".... Start test_127016_no_longitude ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "latitude": 10,
                        "timestamp": get_timestamp()}
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
                assert '' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127016_no_longitude ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少latitude参数")
    @allure.testcase("FT-HTJK-127-017")
    def test_127017_no_latitude(self):
        """ Test get index info without latitude(FT-HTJK-127-017)."""
        self.logger.info(".... Start test_127017_no_latitude ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 10,
                        "timestamp": get_timestamp()}
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
                assert '' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127017_no_latitude ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-127-018")
    def test_127018_no_timestamp(self):
        """ Test get index info without timestamp(FT-HTJK-127-018)."""
        self.logger.info(".... Start test_127018_no_timestamp ....")
        try:
            assert self.token and self.member_id
            with allure.step("teststep1: get parameters."):
                data = {"member_id": self.member_id, "category": 0, "longitude": 1,
                        "latitude": 1}
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
                assert rsp_content["code"] == 101000
                assert 'timestamp值已过期' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_127018_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_APP_GetIndexInfo.py'])
    # pytest.main(['-s', 'test_APP_GetIndexInfo.py::TestGetIndexInfo::test_127018_no_timestamp'])
