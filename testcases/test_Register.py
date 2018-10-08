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
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
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
                             ids=["code_type(0)", "code_type(1)", "code_type(2)", "code_type(3)"])
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
                assert rsp.status_code == 200
                rsp_content = rsp.json()
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
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
