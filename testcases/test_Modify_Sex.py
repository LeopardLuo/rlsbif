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


@allure.feature("修改用户性别")
class TestModifySex(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'ModifySex')
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

            with allure.step("delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", table)
                cls.logger.info("table: {0}".format(table))
                delete_result = cls.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", delete_result)
                cls.logger.info("delete result: {0}".format(delete_result))

            with allure.step("user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222121", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", json)
                cls.logger.info("register params: {0}".format(json))
                register_result = make_register(cls.httpclient, json['client_type'], json['client_version'],
                                       json['device_token'], json['imei'], json['code_type'],
                                        json['phone'], json['sms_code'], json['timestamp'], cls.logger)
                allure.attach("register result", register_result)
                cls.logger.info("register result: {0}".format(register_result))
                cls.token = register_result['token']
                cls.member_id = register_result['member_id']
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
            allure.attach("logout result", logout_result)
            cls.logger.info("logout result: {0}".format(logout_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("critical")
    @allure.story("正确修改性别")
    @allure.testcase("FT-HTJK-108-001")
    def test_108001_modify_sex_correct(self):
        """ Test modify sex by correct parameters(FT-HTJK-108-001)."""
        self.logger.info(".... Start test_108001_modify_sex_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == 1
                assert len(rsp_content["Message"]) == 0

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
                assert info['sex'] == 2
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108001_modify_sex_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-108-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
                             ids=["token(超长值)", "token(小数)", "token(中文)",
                                  "token(特殊字符)", "token(数字中文)",
                                  "token(数字特殊字符)", "token(空格)", "token(空)"])
    def test_108002_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-108-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108002_token_wrong ({0}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 2, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108002_token_wrong ({0}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-108-003")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_108003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-108-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108003_member_id_wrong ({0}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": member_id, "sex": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108003_member_id_wrong ({0}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确sex值")
    @allure.testcase("FT-HTJK-108-004")
    @pytest.mark.parametrize("sex, result",
                             [(1, {"msg": "", "code": "1"}), (2, {"msg": "", "code": "1"}),
                              (3, {"msg": "", "code": "1"})],
                             ids=["sex(1)", "sex(2)", "sex(3)"])
    def test_108004_sex_correct(self, sex, result):
        """ Test correct sex values (1/2/3）(FT-HTJK-108-004).
        :param sex: sex parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108004_sex_correct ({0}) ....".format(sex))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": sex, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
                assert info['sex'] == sex
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108004_sex_correct ({0}) ....".format(sex))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误sex值")
    @allure.testcase("FT-HTJK-108-005")
    @pytest.mark.parametrize("sex, result",
                             [(-1, {"msg": "", "code": ""}), (0, {"msg": "", "code": ""}),
                              (4, {"msg": "", "code": ""}), (-2147483649, {"msg": "", "code": ""}),
                              (2147483648, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('a', {"msg": "", "code": ""}), ('中', {"msg": "", "code": ""}),
                              ('*', {"msg": "", "code": ""}), ('1a', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
                             ids=["sex(1)", "sex(0)", "sex(4)", "sex(-2147483649)", "sex(2147483648)",
                                  "sex(1.0)", "sex(字母)", "sex(中文)", "sex(特殊字符)", "sex(数字字母)",
                                  "sex(数字中文)", "sex(数字特殊字符)", "sex(空格)", "sex(空)"])
    def test_108005_sex_wrong(self, sex, result):
        """ Test sex with wrong values (-1、0、4、-2147483649、2147483648、小数、字母、中文、特殊字符、数字字母、
            数字中文、数字特殊字符、空格、空）(FT-HTJK-108-005).
        :param sex: sex parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108005_sex_wrong ({0}) ....".format(sex))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": sex, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108005_sex_wrong ({0}) ....".format(sex))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-108-006")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 1000, {"msg": "", "code": "1"}),
                              (get_timestamp() + 1000, {"msg": "", "code": "1"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_108006_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-108-006).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108006_timestamp_correct ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 1, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 200)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108006_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-108-007")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"msg": "", "code": ""}), (9223372036854775807, {"msg": "", "code": ""}),
                              (0, {"msg": "", "code": ""}), (-1, {"msg": "", "code": ""}),
                              (-9223372036854775809, {"msg": "", "code": ""}),
                              (9223372036854775808, {"msg": "", "code": ""}),
                              (1.0, {"msg": "", "code": ""}), ('a', {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1a', {"msg": "", "code": ""}), ('1中', {"msg": "", "code": ""}),
                              ('1*', {"msg": "", "code": ""}), (' ', {"msg": "", "code": ""}),
                              ('', {"msg": "", "code": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_108007_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-108-007).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_108007_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 1, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] == result['code']
                assert rsp_content["Message"] == result['msg']

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108007_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-108-008")
    def test_108008_no_token(self):
        """ Test modify sex without token(FT-HTJK-108-008)."""
        self.logger.info(".... Start test_108008_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 2, "timestamp": get_timestamp()}
                headers = {"authorization": ""}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108008_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-108-009")
    def test_108009_no_member_id(self):
        """ Test modify sex without member_id(FT-HTJK-108-009)."""
        self.logger.info(".... Start test_108009_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"sex": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108009_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少sex参数")
    @allure.testcase("FT-HTJK-108-010")
    def test_108010_no_sex(self):
        """ Test modify sex without sex(FT-HTJK-108-010)."""
        self.logger.info(".... Start test_108010_no_sex ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108010_no_sex ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-108-011")
    def test_108011_no_timestamp(self):
        """ Test modify sex without timestamp(FT-HTJK-108-011)."""
        self.logger.info(".... Start test_108011_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "sex": 1}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", info)
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_108011_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-v', '-k', '108001', 'test_Modify_Sex.py'])
    # pytest.main(['-v', 'test_Modify_Sex.py::TestModifySex::test_108001_modify_sex_correct'])
