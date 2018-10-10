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


@allure.feature("退出登录")
class TestLogin(object):

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

            with allure.step("Insert register user info"):
                table = 'member'
                datas = [{'birth_date': '2010-1-10', 'first_name': 'Jimmy', 'last_name': 'Cal', 'gender': 'F',
                          'hire_date': '2018-9-10'},
                         {'birth_date': '2010-2-10', 'first_name': 'Bob', 'last_name': 'TT', 'gender': 'M',
                          'hire_date': '2018-10-10'}]
                allure.attach("table and condition", (table, datas))
                cls.logger.info("table: {0}, condition: {1}".format(table, datas))
                insert_result = cls.mysql.execute_insert(table, datas)
                allure.attach("insert result", insert_result)
                cls.logger.info("insert result: {0}".format(insert_result))
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
        with allure.step("delete all user info"):
            table = 'member'
            allure.attach("table name", table)
            cls.logger.info("table: {0}".format(table))
            delete_result = cls.mysql.execute_delete_all(table)
            allure.attach("delete result", delete_result)
            cls.logger.info("delete result: {0}".format(delete_result))
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
            json = {"code_type": 2, "client_type": 1, "client_version": "0.1", "device_token": "123456789",
                    "imei": "460011234567890", "phone": "13511223001", "sms_code": "1234", "timestamp": get_timestamp()}
            allure.attach("login params value", json)
            self.logger.info("login params: {0}".format(json))
            self.login_result = make_login(self.httpclient, json['code_type'], json['client_type'], json['client_version'],
                                      json['device_token'], json['imei'], json['phone'], json['sms_code'],
                                      json['timestamp'],
                                      self.logger)
            allure.attach("login result", self.login_result)
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization":token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout first time."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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

            with allure.step("teststep5: requests http logout second time."):
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep6: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep7: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
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
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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
                assert len(rsp_content["Message"]) == result['msg']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            token = self.login_result['token']
            self.httpclient.update_header({"token": token})
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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

            with allure.step("teststep4: logout with token empty"):
                self.httpclient.update_header({"token": ""})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", rsp.request.headers)
                allure.attach("request.body", rsp.request.body.decode())
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body.decode()))

            with allure.step("teststep5: assert the response code"):
                allure.attach("Expect response code：", 400)
                allure.attach("Actual response code：", rsp.status_code)
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 400
                rsp_content = rsp.json()

            with allure.step("teststep6: assert the response content"):
                allure.attach("response content：", rsp_content)
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["Code"] != 1
                assert len(rsp_content["Message"]) > 0
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_105004_not_login_token_empty ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-105-005")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"msg": "", "code": ""}), (1.0, {"msg": "", "code": ""}),
                              ('中', {"msg": "", "code": ""}), ('*', {"msg": "", "code": ""}),
                              ('1中', {"msg": "", "code": ""}), ('1*', {"msg": "", "code": ""}),
                              (' ', {"msg": "", "code": ""}), ('', {"msg": "", "code": ""})],
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": get_timestamp()}
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
                assert len(rsp_content["Message"]) == result['msg']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            member_id = self.login_result['user_info']['member_id']
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
            self.logger.info(".... End test_105005_member_id_wrong ({0}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-105-006")
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                self.httpclient.update_header({"authorization": token})
                json = {"member_id": member_id, "timestamp": timestamp}
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
                assert len(rsp_content["Message"]) == result['msg']
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            member_id = self.login_result['user_info']['member_id']
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                self.httpclient.update_header({"authorization": ""})
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
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            token = self.login_result['token']
            self.httpclient.update_header({"token": token})
            member_id = self.login_result['user_info']['member_id']
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"timestamp": get_timestamp()}
                self.httpclient.update_header({"authorization": token})
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
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            token = self.login_result['token']
            self.httpclient.update_header({"token": token})
            member_id = self.login_result['user_info']['member_id']
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
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
                allure.attach("token value", token)
                allure.attach("member_id value", member_id)
                self.logger.info("token: {0}".format(token))
                self.logger.info("member_id: {0}".format(member_id))

            with allure.step("teststep2: requests http logout post."):
                json = {"member_id": member_id}
                self.httpclient.update_header({"authorization": token})
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
        except Exception as e:
            allure.attach("Exception: ", e)
            self.logger.error("Error: exception ocurr: ")
            self.logger.error(e)
            assert False
        finally:
            token = self.login_result['token']
            self.httpclient.update_header({"token": token})
            member_id = self.login_result['user_info']['member_id']
            logout(self.httpclient, member_id, get_timestamp(), self.logger)
            self.logger.info(".... End test_105009_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-v', '-k', '105001', 'test_Logout.py'])
    # pytest.main(['-v', 'test_Logout.py::TestLogout::test_105001_logout_correct'])
