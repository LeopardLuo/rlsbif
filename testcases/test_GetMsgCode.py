#!/usr/bin/env python3
# -*-coding:utf-8-*-

import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient


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
    @allure.testcase("FT-HTJK-001-001")
    def test_001001_get_correct_msg_code(self):
        """ Test get the correct msg code by correct parameters."""
        self.logger.info(".... Start test_001001_get_correct_msg_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"code_type": 0, "phone": "13511220001", "timestamp": get_timestamp()}
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
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
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
        self.logger.info(".... End test_001001_get_correct_msg_code ....")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确code_type值")
    @allure.testcase("FT-HTJK-001-002")
    @pytest.mark.parametrize("code_type, phone, result",
                             [(0, "13511220002", {"code": 1, "msg": ""}), (1, "13511220003", {"code": 1, "msg": ""}),
                              (2, "13511220004", {"code": 1, "msg": ""}), (3, "13511220005", {"code": 1, "msg": ""}),
                              (4, "13511220006", {"code": 1, "msg": ""})],
                             ids=["code_type(0)", "code_type(1)", "code_type(2)", "code_type(3)", "code_type(4)"])
    def test_001002_codetype_correct(self, code_type, phone, result):
        """ Test correct code_type values (0, 1, 2, 3, 4).
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_001002_codetype_correct ....")
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
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
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
        self.logger.info(".... End test_001002_codetype_correct ....")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_type值")
    @allure.testcase("FT-HTJK-001-003")
    @pytest.mark.parametrize("code_type, phone, result",
                             [(-1, "13511220007", {"msg": "", "result": ""}), (5, "13511220008", {"msg": "", "result": ""}),
                              (-2147483649, "13511220009", {"msg": "", "result": ""}), (2147483648, "13511220010", {"msg": "", "result": ""}),
                              (1.0, "13511220011", {"msg": "", "result": ""}), ('a', "13511220012", {"msg": "", "result": ""}),
                              ('中', "13511220013", {"msg": "", "result": ""}), ('*', "13511220014", {"msg": "", "result": ""}),
                              ('1a', "13511220015", {"msg": "", "result": ""}), ('1中', "13511220016", {"msg": "", "result": ""}),
                              ('1*', "13511220017", {"msg": "", "result": ""}), (' ', "13511220018", {"msg": "", "result": ""}),
                              ('', "13511220019", {"msg": "", "result": ""}),],
                             ids=["code_type(0)", "code_type(1)", "code_type(2)", "code_type(3)", "code_type(4)"])
    def test_001002_codetype_correct(self, code_type, phone, result):
        """ Test correct code_type values (-1、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）.
        :param code_type: code_type parameter value.
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_001002_codetype_correct ....")
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
                allure.attach("response content：", rsp_content)
                self.logger.info("response code: {}".format(rsp.status_code))
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
        self.logger.info(".... End test_001002_codetype_correct ....")
        self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_template.py'])
