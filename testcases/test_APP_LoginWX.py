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
@allure.feature("APP-登录-微信授权")
class TestWXLogin(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'WXLogin')
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
                        "imei": "460011234567890", "phone": "13511222401", "sms_code": "123456",
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

    # @allure.severity("critical")
    # @allure.story("登录成功")
    # @allure.testcase("FT-HTJK-104-001")
    # def test_104001_WXlogin_correct(self):
    #     """ Test wx login by correct parameters(FT-HTJK-104-001)."""
    #     self.logger.info(".... Start test_104001_WXlogin_correct ....")
    #     try:
    #         with allure.step("teststep1: get parameters."):
    #             json = {"client_type": 1, "client_version": "v1", "device_token": "460011234567890",
    #                     "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe", "timestamp": get_timestamp()}
    #             allure.attach("params value", str(json))
    #             self.logger.info("params: {0}".format(json))
    #
    #         with allure.step("teststep2: requests http post."):
    #             rsp = self.httpclient.post(self.URI, json=json)
    #             allure.attach("request.headers", str(rsp.request.headers))
    #             allure.attach("request.body", str(rsp.request.body))
    #             self.logger.info("request.headers: {}".format(rsp.request.headers))
    #             self.logger.info("request.body: {}".format(rsp.request.body))
    #
    #         with allure.step("teststep4: assert the response code"):
    #             allure.attach("Expect response code：", '200')
    #             allure.attach("Actual response code：", str(rsp.status_code))
    #             self.logger.info("Actual response code：{0}".format(rsp.status_code))
    #             assert rsp.status_code == 200
    #             rsp_content = rsp.json()
    #
    #         with allure.step("teststep5: assert the response content"):
    #             allure.attach("response content：", str(rsp_content))
    #             self.logger.info("response content: {}".format(rsp_content))
    #             assert rsp_content["code"] == 1
    #             assert '' in rsp_content["message"]
    #             assert rsp_content["result"]["token"]
    #     except Exception as e:
    #         allure.attach("Exception: ", "{}".format(e))
    #         self.logger.error("Error: exception occur: ")
    #         self.logger.error(e)
    #         assert False
    #     finally:
    #         self.logger.info(".... End test_104001_WXlogin_correct ....")
    #         self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_type值")
    @allure.testcase("FT-HTJK-104-003")
    @pytest.mark.parametrize("client_type, result",
                             [(-1, {"status": 200, "msg": "client_type值非法", "code": 101000}),
                              (15, {"status": 200, "msg": "获取授权失败", "code": 201103}),
                              (-2147483649, {"status": 400, "msg": "", "code": 0}),
                              (2147483648, {"status": 400, "msg": "", "code": 0}),
                              (1.0, {"status": 400, "msg": "", "code": 0}),
                              ('a', {"status": 400, "msg": "", "code": 0}),
                              ('中', {"status": 400, "msg": "", "code": 0}),
                              ('*', {"status": 400, "msg": "", "code": 0}),
                              ('1a', {"status": 400, "msg": "", "code": 0}),
                              ('1中', {"status": 400, "msg": "", "code": 0}),
                              ('1*', {"status": 400, "msg": "", "code": 0}),
                              (' ', {"status": 400, "msg": "", "code": 0}),
                              ('', {"status": 400, "msg": "", "code": 0})],
                             ids=["client_type(-1)", "client_type(4)", "client_type(超小值)", "client_type(超大值)",
                                  "client_type(小数)", "client_type(字母)", "client_type(中文)",
                                  "client_type(特殊字符)", "client_type(数字字母)", "client_type(数字中文)",
                                  "client_type(数字特殊字符)", "client_type(空格)", "client_type(空)"])
    def test_104003_clienttype_wrong(self, client_type, result):
        """ Test wrong client_type values (-1、4、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-104-003).
        :param client_type: client_type parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104003_clienttype_wrong ({}) ....".format(client_type))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": client_type, "client_version": "v1", "device_token": "460011234567890",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104003_clienttype_wrong ({}) ....".format(client_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误client_version值")
    @allure.testcase("FT-HTJK-104-005")
    @pytest.mark.parametrize("client_version, result",
                             [('1' * 1001, {"msg": "获取授权失败", "code": 201103}),
                              (' ', {"msg": "client_version不能为空", "code": 101000}),
                              ('', {"msg": "client_version不能为空", "code": 101000})],
                             ids=["client_version(超长值)", "client_version(空格)", "client_version(空)"])
    def test_104005_clientversion_wrong(self, client_version, result):
        """ Test wrong client_type values (超长值、空格、空）(FT-HTJK-104-005).
        :param client_version: client_version parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104005_clientversion_wrong ({}) ....".format(client_version))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": client_version, "device_token": "460011234567890",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104005_clientversion_wrong ({}) ....".format(client_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误device_token值")
    @allure.testcase("FT-HTJK-104-007")
    @pytest.mark.parametrize("device_token, result",
                             [('1' * 256, {"code": 101000, "msg": "device_token值非法"}),
                              (' ', {"code": 101000, "msg": "不能为空"}), ('', {"code": 101000, "msg": "不能为空"})],
                             ids=["device_token(超长值)", "device_token(空格)", "device_token(空)"])
    def test_104007_devicetoken_wrong(self, device_token, result):
        """ Test wrong device_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-104-007).
        :param device_token: device_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104007_devicetoken_wrong ({}) ....".format(device_token))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": device_token,
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104007_devicetoken_wrong ({}) ....".format(device_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误imei值")
    @allure.testcase("FT-HTJK-104-009")
    @pytest.mark.parametrize("imei, result",
                             [('1' * 18, {"code": 201103, "msg": "获取授权失败"}), (12345678901234.0, {"code": 201103, "msg": "获取授权失败"}),
                              ('a' * 15, {"code": 201103, "msg": "获取授权失败"}), ('中' * 15, {"code": 201103, "msg": "获取授权失败"}),
                              ('*' * 15, {"code": 201103, "msg": "获取授权失败"}), ('1a' * 8, {"code": 201103, "msg": "获取授权失败"}),
                              ('1中' * 8, {"code": 201103, "msg": "获取授权失败"}), ('1*' * 8, {"code": 201103, "msg": "获取授权失败"}),
                              (' ' * 15, {"code": 101000, "msg": "imei值非法"}), ('', {"code": 101000, "msg": "imei值非法"})],
                             ids=["imei(超长值)", "imei(小数)", "imei(字母)", "imei(中文)",
                                  "imei(特殊字符)", "imei(数字字母)", "imei(数字中文)",
                                  "imei(数字特殊字符)", "imei(空格)", "imei(空)"])
    def test_104009_imei_wrong(self, imei, result):
        """ Test wrong imei values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-104-009).
        :param imei: imei parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104009_imei_wrong ({}) ....".format(imei))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": "460011234567890",
                        "imei": imei, "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104009_imei_wrong ({}) ....".format(imei))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code值")
    @allure.testcase("FT-HTJK-104-010")
    @pytest.mark.parametrize("code, result",
                             [('1' * 256, {"code": 201103, "msg": "获取授权失败"}), (1.0, {"code": 201103, "msg": "获取授权失败"}),
                              ('a', {"code": 201103, "msg": "获取授权失败"}), ('中', {"code": 201103, "msg": "获取授权失败"}),
                              ('*', {"code": 201103, "msg": "获取授权失败"}), ('1a', {"code": 201103, "msg": "获取授权失败"}),
                              ('1中', {"code": 201103, "msg": "获取授权失败"}), ('1*', {"code": 201103, "msg": "获取授权失败"}),
                              (' ', {"code": 101000, "msg": "code值非法"}), ('', {"code": 101000, "msg": "code值非法"})],
                             ids=["code(超长值)", "code(小数)", "code(字母)", "code(中文)",
                                  "code(特殊字符)", "code(数字字母)", "code(数字中文)",
                                  "code(数字特殊字符)", "code(空格)", "code(空)"])
    def test_104010_code_wrong(self, code, result):
        """ Test wrong code values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-104-010).
        :param code: code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104010_code_wrong ({}) ....".format(code))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": "460011234567890",
                        "imei": "460011234567890", "code": code,
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104010_code_wrong ({}) ....".format(code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-104-012")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 201103, "msg": "获取授权失败"}),
                              (9223372036854775807, {"status": 200, "code": 201103, "msg": "获取授权失败"}),
                              (0, {"status": 200, "code": 101000, "msg": "timestamp不能为空"}),
                              (-1, {"status": 200, "code": 201103, "msg": "获取授权失败"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 200, "code": 201103, "msg": "获取授权失败"}),
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
    def test_104012_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-104-012).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_104012_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": 'v1', "device_token": "460011234567890",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": timestamp}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Expect response code：", '200')
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104012_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_type参数")
    @allure.testcase("FT-HTJK-104-013")
    def test_104013_no_clienttype(self):
        """ Test login without client_type(FT-HTJK-104-013)."""
        self.logger.info(".... Start test_104013_no_clienttype ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_version": 'v1', "device_token": "460011234567890",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 201103
                    assert '获取授权失败' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104013_no_clienttype ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少client_version参数")
    @allure.testcase("FT-HTJK-104-014")
    def test_104014_no_client_version(self):
        """ Test login without client_version(FT-HTJK-104-014)."""
        self.logger.info(".... Start test_104014_no_client_version ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "device_token": "460011234567890",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 101000
                    assert 'client_version不能为空' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104014_no_client_version ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少device_token参数")
    @allure.testcase("FT-HTJK-104-015")
    def test_104015_no_device_token(self):
        """ Test login without device_token(FT-HTJK-104-015)."""
        self.logger.info(".... Start test_104015_no_device_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": "v1",
                        "imei": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 101000
                    assert '不能为空' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104015_no_device_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少imei参数")
    @allure.testcase("FT-HTJK-104-016")
    def test_104016_no_imei(self):
        """ Test login without imei(FT-HTJK-104-016)."""
        self.logger.info(".... Start test_104016_no_imei ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": "v1",
                        "device_token": "460011234567890", "code": "071mBhQ108XUcE1jblN105mSP10mBhe",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 101000
                    assert 'imei值非法' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104016_no_imei ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少code参数")
    @allure.testcase("FT-HTJK-104-017")
    def test_104017_no_code(self):
        """ Test login without code(FT-HTJK-104-017)."""
        self.logger.info(".... Start test_104017_no_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": "v1",
                        "device_token": "460011234567890", "imei": "460011234567890",
                        "timestamp": get_timestamp()}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 101000
                    assert 'code值非法' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104017_no_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-104-018")
    def test_104018_no_timestamp(self):
        """ Test login without timestamp(FT-HTJK-104-018)."""
        self.logger.info(".... Start test_104018_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"client_type": 1, "client_version": "v1",
                        "device_token": "460011234567890", "imei": "460011234567890",
                        "code": '071mBhQ108XUcE1jblN105mSP10mBhe'}
                allure.attach("params value", str(json))
                self.logger.info("params: {0}".format(json))

            with allure.step("teststep2: requests http post."):
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == 101000
                    assert 'timestamp不能为空' in rsp_content["message"]
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_104018_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_LoginWX.py'])
    pytest.main(['-s', 'test_APP_LoginWX.py::TestWXLogin::test_104018_no_timestamp'])
