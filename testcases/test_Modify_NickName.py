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


@allure.feature("修改用户昵称")
class TestModifyNickName(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'ModifyNickName')
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
                        "imei": "460011234567890", "phone": "13511222111", "sms_code": "123456",
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
    @allure.story("正确修改昵称")
    @allure.testcase("FT-HTJK-107-001")
    def test_107001_modify_nickname_correct(self):
        """ Test modify nick name by correct parameters(FT-HTJK-107-001)."""
        self.logger.info(".... Start test_107001_modify_nickname_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": "GoodName", "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] == "GoodName"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107001_modify_nickname_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-107-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
                             ids=["token(超长值)", "token(小数)", "token(中文)",
                                  "token(特殊字符)", "token(数字中文)",
                                  "token(数字特殊字符)", "token(空格)", "token(空)"])
    def test_107002_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-107-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107002_token_wrong ({0}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": "TokenName", "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "TokenName"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107002_token_wrong ({0}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-107-003")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_107003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-107-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107003_member_id_wrong ({0}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": member_id, "nickname": "MemberIdName", "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "MemberIdName"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107003_member_id_wrong ({0}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确nickname值")
    @allure.testcase("FT-HTJK-107-004")
    @pytest.mark.parametrize("nickname, result",
                             [('1', {"msg": "", "code": "1"}), ('1' * 256, {"msg": "", "code": "1"}),
                              ('a', {"msg": "", "code": "1"}), ('中', {"msg": "", "code": "1"}),
                              ('*', {"msg": "", "code": "1"}), ('1a*中', {"msg": "", "code": "1"}),
                              (' ', {"msg": "", "code": "1"}), ('', {"msg": "", "code": "1"})],
                             ids=["nickname(最小长度值)", "nickname(最大长度值)", "nickname(字母)",
                                  "nickname(中文)", "nickname(特殊字符)", "nickname(数字字母中文特殊字符)",
                                  "nickname(空格)", "nickname(空)"])
    def test_107004_nickname_correct(self, nickname, result):
        """ Test correct nickname values (最小长度值、最大长度值、字母、中文、特殊字符、数字字母中文特殊字符、空格、空）(FT-HTJK-107-004).
        :param nickname: nickname parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107004_nickname_correct ({0}) ....".format(nickname))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": nickname, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] == nickname
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107004_nickname_correct ({0}) ....".format(nickname))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误nickname值")
    @allure.testcase("FT-HTJK-107-005")
    @pytest.mark.parametrize("nickname, result",
                             [(1.0, {"msg": "", "code": "1"}), ('1' * 256, {"msg": "", "code": "1"})],
                             ids=["nickname(小数)", "nickname(超长值)"])
    def test_107005_nickname_wrong(self, nickname, result):
        """ Test wrong nickname values (小数、超长值）(FT-HTJK-107-005).
        :param nickname: nickname parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107005_nickname_wrong ({0}) ....".format(nickname))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": nickname, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != nickname
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107005_nickname_wrong ({0}) ....".format(nickname))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-107-006")
    @pytest.mark.parametrize("timestamp, nickname, result",
                             [(get_timestamp() - 1000, 'name1', {"msg": "", "code": "1"}),
                              (get_timestamp() + 1000, 'name2', {"msg": "", "code": "1"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_107006_timestamp_correct(self, timestamp, nickname, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-107-006).
        :param timestamp: timestamp parameter value.
        :param nickname: nickname parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107006_timestamp_correct ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": nickname, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] == nickname
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107006_timestamp_correct ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-107-007")
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
    def test_107007_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-107-007).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_107007_timestamp_wrong ({0}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": "TimestampName", "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "TimestampName"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107007_timestamp_wrong ({0}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-107-008")
    def test_107008_no_token(self):
        """ Test modify nickname without token(FT-HTJK-107-008)."""
        self.logger.info(".... Start test_107008_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": "NoToken", "timestamp": get_timestamp()}
                headers = {"authorization": ""}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "NoToken"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107008_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-107-009")
    def test_107009_no_member_id(self):
        """ Test modify nickname without member_id(FT-HTJK-107-009)."""
        self.logger.info(".... Start test_107009_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"nickname": "NoMemberId", "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "NoMemberId"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107009_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少nickname参数")
    @allure.testcase("FT-HTJK-107-010")
    def test_107010_no_nickname(self):
        """ Test modify nickname without nickname(FT-HTJK-107-010)."""
        self.logger.info(".... Start test_107010_no_nickname ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != ""
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107010_no_nickname ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-107-011")
    def test_107011_no_timestamp(self):
        """ Test modify nickname without timestamp(FT-HTJK-107-011)."""
        self.logger.info(".... Start test_107011_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "nickname": "NoTimestamp"}
                headers = {"authorization": self.token}
                allure.attach("params value", (json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http get."):
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
                assert info['nickname'] != "NoTimestamp"
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_107011_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-v', '-k', '107001', 'test_Modify_NickName.py'])
    # pytest.main(['-v', 'test_Modify_NickName.py::TestModifyNickName::test_107001_modify_nickname_correct'])
