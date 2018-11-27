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


@allure.feature("APP-修改手机号")
class TestModifyPhone(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'ModifyPhone')
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

    @allure.step("+++ setup method +++")
    def setup_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start setup method ===")
        self.logger.info(method.__name__)
        with allure.step("delete insert user info"):
            table = 'mem_member'
            condition = ("phone", "1351122%")
            allure.attach("table name", str(table))
            self.logger.info("table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))

        with allure.step("user register."):
            json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                    "imei": "460011234567890", "phone": "13511222141", "sms_code": "123456",
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
        self.logger.info("=== End setup method ===")
        self.logger.info("")

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        with allure.step("user logout."):
            self.httpclient.update_header({"authorization": self.token})
            logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
            self.httpclient.update_header({"authorization": None})
            allure.attach("logout result", str(logout_result))
            self.logger.info("logout result: {0}".format(logout_result))
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确修改手机号")
    @allure.testcase("FT-HTJK-112-001")
    def test_112001_modify_phone_correct(self):
        """ Test modify phone by correct parameters(FT-HTJK-112-001)."""
        self.logger.info(".... Start test_112001_modify_phone_correct ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token, get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 1
                assert '修改用户手机成功' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112001_modify_phone_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("未验证手机号修改手机号")
    @allure.testcase("FT-HTJK-112-002")
    def test_112002_modify_phone_without_verify(self):
        """ Test modify phone without get msg code(FT-HTJK-112-002)."""
        self.logger.info(".... Start test_112002_modify_phone_without_verify ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222143", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 201109
                assert '当前手机号码与验证手机号不符' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112002_modify_phone_without_verify ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-112-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_112003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112003_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112003_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-112-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 200, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}), ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_112004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112004_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": member_id, "phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112004_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone值")
    @allure.testcase("FT-HTJK-112-005")
    @pytest.mark.parametrize("phone, result",
                             [("1", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("135123456789", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("0", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("-1", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("135112210.0", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("1" * 256, {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("a", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("中", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("*", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("1351122105a", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("1351122105中", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              ("1351122105*", {"code": 201109, "msg": "当前手机号码与验证手机号不符"}),
                              (" ", {"code": 101000, "msg": "phone值非法"}),
                              ("", {"code": 101000, "msg": "phone值非法"})],
                             ids=["phone(1)", "phone(12位)", "phone(0)", "phone(-1)", "phone(小数)", "phone(超长值)",
                                  "phone(字母)", "phone(中文)", "phone(特殊字符)", "phone(数字字母)", "phone(数字中文)",
                                  "phone(数字特殊字符)", "phone(空格)", "phone(空)"])
    def test_112005_phone_wrong(self, phone, result):
        """ Test wrong phone values (1、12位、0、-1、小数、超长值、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-005).
        :param phone: phone parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112005_phone_wrong ({}) ....".format(phone))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": phone, "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112005_phone_wrong ({}) ....".format(phone))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误sms_code值")
    @allure.testcase("FT-HTJK-112-006")
    @pytest.mark.parametrize("sms_code, result",
                             [('1' * 256, {"code": 201106, "msg": "验证码不正确"}),
                              ('1.0', {"code": 201106, "msg": "验证码不正确"}),
                              ('a', {"code": 201106, "msg": "验证码不正确"}),
                              ('中', {"code": 201106, "msg": "验证码不正确"}),
                              ('*', {"code": 201106, "msg": "验证码不正确"}),
                              ('1a', {"code": 201106, "msg": "验证码不正确"}),
                              ('1中', {"code": 201106, "msg": "验证码不正确"}),
                              ('1*', {"code": 201106, "msg": "验证码不正确"}),
                              (' ', {"code": 101000, "msg": "sms_code值非法"}),
                              ('', {"code": 101000, "msg": "sms_code值非法"})],
                             ids=["sms_code(超长值)", "sms_code(小数)", "sms_code(字母)", "sms_code(中文)",
                                  "sms_code(特殊字符)", "sms_code(数字字母)", "sms_code(数字中文)",
                                  "sms_code(数字特殊字符)", "sms_code(空格)", "sms_code(空)"])
    def test_112006_smscode_wrong(self, sms_code, result):
        """ Test wrong sms_code values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-006).
        :param sms_code: sms_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112006_smscode_wrong ({}) ....".format(sms_code))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142", "sms_code": sms_code,
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112006_smscode_wrong ({}) ....".format(sms_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误code_token值")
    @allure.testcase("FT-HTJK-112-007")
    @pytest.mark.parametrize("code_token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}),
                              ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('a', {"code": 201001, "msg": "授权非法"}),
                              ('中', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}),
                              ('1a', {"code": 201001, "msg": "授权非法"}),
                              ('1中', {"code": 201001, "msg": "授权非法"}),
                              ('1*', {"code": 201001, "msg": "授权非法"}),
                              (' ', {"code": 101000, "msg": "code_token值非法"}),
                              ('', {"code": 101000, "msg": "code_token值非法"})],
                             ids=["code_token(超长值)", "code_token(小数)", "code_token(字母)", "code_token(中文)",
                                  "code_token(特殊字符)", "code_token(数字字母)", "code_token(数字中文)",
                                  "code_token(数字特殊字符)", "code_token(空格)", "code_token(空)"])
    def test_112007_codetoken_wrong(self, code_token, result):
        """ Test wrong code_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-007).
        :param code_token: code_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112007_codetoken_wrong ({}) ....".format(code_token))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                assert code_token1

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token1,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142", "sms_code": '123456',
                        "code_token": code_token, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112007_codetoken_wrong ({}) ....".format(code_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误phone_token值")
    @allure.testcase("FT-HTJK-112-008")
    @pytest.mark.parametrize("phone_token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}),
                              ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('a', {"code": 201001, "msg": "授权非法"}),
                              ('中', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}),
                              ('1a', {"code": 201001, "msg": "授权非法"}),
                              ('1中', {"code": 201001, "msg": "授权非法"}),
                              ('1*', {"code": 201001, "msg": "授权非法"}),
                              (' ', {"code": 101000, "msg": "phone_token值非法"}),
                              ('', {"code": 101000, "msg": "phone_token值非法"})],
                             ids=["phone_token(超长值)", "phone_token(小数)", "phone_token(字母)", "phone_token(中文)",
                                  "phone_token(特殊字符)", "phone_token(数字字母)", "phone_token(数字中文)",
                                  "phone_token(数字特殊字符)", "phone_token(空格)", "phone_token(空)"])
    def test_112008_phone_token_wrong(self, phone_token, result):
        """ Test wrong phone_token values (超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-008).
        :param phone_token: phone_token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112008_phone_token_wrong ({}) ....".format(phone_token))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                assert code_token1

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token1,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142", "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112008_phone_token_wrong ({}) ....".format(phone_token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-112-009")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": "修改用户手机成功"}),
                              (get_timestamp() + 300, {"code": 1, "msg": "修改用户手机成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_112009_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-112-009).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112009_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                assert code_token1

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token1,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142", "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112009_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-112-010")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 0, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": ""}), (-1, {"status": 200, "code": 0, "msg": ""}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 200, "code": 0, "msg": ""}),
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
    def test_112010_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-112-010).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_112010_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token1 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token1))
                self.logger.info("getmsgcode result: {0}".format(code_token1))
                assert code_token1

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token1,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142", "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112010_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-112-011")
    def test_112011_no_token(self):
        """ Test modify phone without token(FT-HTJK-112-011)."""
        self.logger.info(".... Start test_112011_no_token ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 201000
                assert '未登录或登录已过期' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112011_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-112-012")
    def test_112012_no_member_id(self):
        """ Test modify phone without member_id(FT-HTJK-112-012)."""
        self.logger.info(".... Start test_112012_no_member_id ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"phone": '13511222142', "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 201301
                assert '非该用户的认证手机号码' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112012_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少phone参数")
    @allure.testcase("FT-HTJK-112-013")
    def test_112013_no_phone(self):
        """ Test modify phone without phone(FT-HTJK-112-013)."""
        self.logger.info(".... Start test_112013_no_phone ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "sms_code": '123456',
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 101000
                assert 'phone值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112013_no_phone ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少sms_code参数")
    @allure.testcase("FT-HTJK-112-014")
    def test_112014_no_sms_code(self):
        """ Test modify phone without sms_code(FT-HTJK-112-014)."""
        self.logger.info(".... Start test_112014_no_sms_code ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142",
                        "code_token": code_token2, "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 101000
                assert 'sms_code值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112014_no_sms_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少code_token参数")
    @allure.testcase("FT-HTJK-112-015")
    def test_112015_no_code_token(self):
        """ Test modify phone without code_token(FT-HTJK-112-015)."""
        self.logger.info(".... Start test_112015_no_code_token ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142",
                        "sms_code": '123456', "phone_token": phone_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 101000
                assert 'code_token值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112015_no_code_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少phone_token参数")
    @allure.testcase("FT-HTJK-112-016")
    def test_112016_no_phone_token(self):
        """ Test modify phone without phone_token(FT-HTJK-112-016)."""
        self.logger.info(".... Start test_112016_no_phone_token ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142",
                        "sms_code": '123456', "code_token": code_token2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 101000
                assert 'phone_token值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112016_no_phone_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-112-017")
    def test_112017_no_timestamp(self):
        """ Test modify phone without timestamp(FT-HTJK-112-017)."""
        self.logger.info(".... Start test_112017_no_timestamp ....")
        try:
            with allure.step("teststep1: get check msg code."):
                params = {"code_type": 4, "phone": "13511222141", "timestamp": get_timestamp()}
                allure.attach("get check msgcode params value", str(params))
                self.logger.info("get check msgcode params: {0}".format(params))
                code_token = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                          self.logger)
                allure.attach("getmsgcode result", str(code_token))
                self.logger.info("getmsgcode result: {0}".format(code_token))
                assert code_token

            with allure.step("teststep2: check old phone."):
                json = {"member_id": self.member_id, "phone": '13511222141', "sms_code": '123456',
                        "code_token": code_token, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                check_result = check_phone(self.httpclient, self.member_id, '13511222141', '123456', code_token,
                                           get_timestamp(), self.logger)
                allure.attach("check phone result", str(check_result))
                self.logger.info("check_result: {}".format(check_result))
                assert check_result
                phone_token = check_result['phone_token']

            with allure.step("teststep3: get modify msg code."):
                params = {"code_type": 1, "phone": "13511222142", "timestamp": get_timestamp()}
                allure.attach("get modify msgcode params value", str(params))
                self.logger.info("\nget modify msgcode params: {0}".format(params))
                code_token2 = get_msg_code(self.httpclient, params["code_type"], params["phone"], params["timestamp"],
                                           self.logger)
                allure.attach("getmsgcode result", str(code_token2))
                self.logger.info("getmsgcode result: {0}".format(code_token2))
                assert code_token2

            with allure.step("teststep4: get parameters."):
                json = {"member_id": self.member_id, "phone": "13511222142",
                        "sms_code": '123456', "code_token": code_token2, "phone_token": phone_token}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("\ndata: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep5: requests http post."):
                self.httpclient.update_header(headers)
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
                assert rsp_content["code"] == 101000
                assert 'timestamp不能为空' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_112017_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Modify_Phone.py'])
    pytest.main(['-s', 'test_APP_Modify_Phone.py::TestModifyPhone::test_112017_no_timestamp'])
