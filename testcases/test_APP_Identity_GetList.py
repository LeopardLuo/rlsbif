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


@allure.feature("APP-获取关联人列表")
class TestGetIdentityList(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'GetIdentityOtherList')
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
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511222181", "sms_code": "123456",
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

            with allure.step("teststep: user feature."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_myfeature(cls.httpclient, cls.member_id, 'face2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                cls.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep: identity user."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_identity(cls.httpclient, cls.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                cls.logger.info("identity owner result: {0}".format(identity_result))
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
        with allure.step("user logout."):
            cls.httpclient.update_header({"authorization": cls.token})
            logout_result = logout(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
            cls.httpclient.update_header({"authorization": None})
            allure.attach("logout result", str(logout_result))
            cls.logger.info("logout result: {0}".format(logout_result))
        with allure.step("teststep: delete user identity record"):
            table = 'mem_features'
            condition = ("member_id", cls.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            cls.logger.info("")
            cls.logger.info("table: {0}, condition: {1}".format(table, condition))
            select_result = cls.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(select_result))
            cls.logger.info("delete result: {0}".format(select_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("critical")
    @allure.story("2页获取1页")
    @allure.testcase("FT-HTJK-116-001")
    def test_116001_relatives_2page_1index(self):
        """ Test get list 1 index in 2 pages(FT-HTJK-116-001)."""
        self.logger.info(".... Start test_116001_relatives_2page_1index ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg', 'face2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))
                identity_result2 = identity_other(self.httpclient, self.member_id, 'kuli2', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result2))
                self.logger.info("identity_result: {0}".format(identity_result2))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']['data']
                assert rsp_content['result']['page']['page_index'] == 0
                assert rsp_content['result']['page']['page_size'] == 1
                assert rsp_content['result']['page']['total_count'] == 2
                assert rsp_content['result']['page']['total_page'] == 2
                assert rsp_content['result']['page']['has_next_page']
                assert not rsp_content['result']['page']['has_previous_page']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("delete database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                select_result = self.mysql.execute_select_condition(table, condition)
                for member in select_result:
                    if member[2] != '本人':
                        condition = ("features_id", member[0])
                        allure.attach("table name and condition", "{0},{1}".format(table, condition))
                        self.logger.info("")
                        self.logger.info("table: {0}, condition: {1}".format(table, condition))
                        delete_result = self.mysql.execute_delete_condition(table, condition)
                        allure.attach("delete result", str(delete_result))
                        self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_116001_relatives_2page_1index ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("2页获取2页")
    @allure.testcase("FT-HTJK-116-002")
    def test_116002_relatives_2page_2index(self):
        """ Test get list 2 index in 2 pages(FT-HTJK-116-002)."""
        self.logger.info(".... Start test_116002_relatives_2page_2index ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))
                identity_result2 = identity_other(self.httpclient, self.member_id, 'kuli2', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result2))
                self.logger.info("identity_result: {0}".format(identity_result2))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']['data']
                assert rsp_content['result']['page']['page_index'] == 1
                assert rsp_content['result']['page']['page_size'] == 1
                assert rsp_content['result']['page']['total_count'] == 2
                assert rsp_content['result']['page']['total_page'] == 2
                assert not rsp_content['result']['page']['has_next_page']
                assert rsp_content['result']['page']['has_previous_page']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("delete database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                select_result = self.mysql.execute_select_condition(table, condition)
                for member in select_result:
                    if member[2] != '本人':
                        condition = ("features_id", member[0])
                        allure.attach("table name and condition", "{0},{1}".format(table, condition))
                        self.logger.info("")
                        self.logger.info("table: {0}, condition: {1}".format(table, condition))
                        delete_result = self.mysql.execute_delete_condition(table, condition)
                        allure.attach("delete result", str(delete_result))
                        self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_116002_relatives_2page_2index ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人列表空")
    @allure.testcase("FT-HTJK-116-003")
    def test_116003_relatives_list_empty(self):
        """ Test identity relatives by correct parameters(FT-HTJK-116-003)."""
        self.logger.info(".... Start test_116003_relatives_list_empty ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert not rsp_content['result']['data']
                assert rsp_content['result']['page']['page_index'] == 0
                assert rsp_content['result']['page']['page_size'] == 2
                assert rsp_content['result']['page']['total_count'] == 0
                assert rsp_content['result']['page']['total_page'] == 0
                assert not rsp_content['result']['page']['has_next_page']
                assert not rsp_content['result']['page']['has_previous_page']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116003_relatives_list_empty ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-116-004")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 0, "msg": "授权非法"}), ('1.0', {"code": 0, "msg": "授权非法"}),
                              ('*', {"code": 0, "msg": "授权非法"}), ('1*', {"code": 0, "msg": "授权非法"}),
                              ('', {"code": 0, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_116004_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-116-004).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116004_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116004_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-116-005")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
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
    def test_116005_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-116-005).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116005_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": member_id, "page_index": 1, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116005_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误page_index值")
    @allure.testcase("FT-HTJK-116-006")
    @pytest.mark.parametrize("page_index, result",
                             [(-1, {"status": 200, "code": 0, "msg": "not valid"}),
                              (-2147483649, {"status": 400, "code": 0, "msg": "not valid"}),
                              (2147483648, {"status": 400, "code": 0, "msg": "not valid"}),
                              (1.0, {"status": 400, "code": 0, "msg": "not valid"}),
                              ('a', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('中', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('*', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "not valid"}),
                              (' ', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('', {"status": 400, "code": 0, "msg": "not valid"})],
                             ids=["page_index(-1)",
                                  "page_index(-2147483649)", "page_index(2147483648)", "page_index(小数)",
                                  "page_index(字母)", "page_index(中文)", "page_index(特殊字符)",
                                  "page_index(数字字母)", "page_index(数字中文)",
                                  "page_index(数字特殊字符)", "page_index(空格)", "page_index(空)"])
    def test_116006_page_index_wrong(self, page_index, result):
        """ Test wrong page_index values (-1、0、5、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-116-006).
        :param page_index: page_index parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116006_page_index_wrong ({}) ....".format(page_index))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": page_index, "page_size": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116006_page_index_wrong ({}) ....".format(page_index))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确page_size值")
    @allure.testcase("FT-HTJK-116-007")
    @pytest.mark.parametrize("page_size, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2147483647, {"status": 200, "code": 1, "msg": ""})],
                             ids=["page_size(最小值)", "page_size(最大值)"])
    def test_116007_page_size_correct(self, page_size, result):
        """ Test correct page_size values (最小值,最大值）(FT-HTJK-116-007).
        :param page_size: page_size parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116007_page_size_correct ({}) ....".format(page_size))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": page_size,
                          "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116007_page_size_correct ({}) ....".format(page_size))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误page_size值")
    @allure.testcase("FT-HTJK-116-008")
    @pytest.mark.parametrize("page_size, result",
                             [(-1, {"status": 200, "code": 0, "msg": "not valid"}),
                              (0, {"status": 200, "code": 0, "msg": "not valid"}),
                              (-2147483649, {"status": 400, "code": 0, "msg": "not valid"}),
                              (2147483648, {"status": 400, "code": 0, "msg": "not valid"}),
                              (1.0, {"status": 400, "code": 0, "msg": "not valid"}),
                              ('a', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('中', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('*', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "not valid"}),
                              (' ', {"status": 400, "code": 0, "msg": "not valid"}),
                              ('', {"status": 400, "code": 0, "msg": "not valid"})],
                             ids=["page_size(-1)", "page_size(0)",
                                  "page_size(-2147483649)", "page_size(2147483648)", "page_size(小数)",
                                  "page_size(字母)", "page_size(中文)", "page_size(特殊字符)",
                                  "page_size(数字字母)", "page_size(数字中文)",
                                  "page_size(数字特殊字符)", "page_size(空格)", "page_size(空)"])
    def test_116008_page_size_wrong(self, page_size, result):
        """ Test wrong page_size values (-1、0、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-116-006).
        :param page_size: page_size parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116008_page_size_wrong ({}) ....".format(page_size))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": page_size,
                          "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116008_page_size_wrong ({}) ....".format(page_size))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-116-009")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 10000, {"code": 1, "msg": ""}),
                              (get_timestamp() + 1000, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_116009_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-116-009).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116009_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1,
                          "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116009_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-116-010")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 0, "msg": "is invalid"}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": "is invalid"}),
                              (0, {"status": 200, "code": 0, "msg": "is invalid"}),
                              (-1, {"status": 200, "code": 0, "msg": "is invalid"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (1.0, {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              (' ', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('', {"status": 400, "code": 0, "msg": "is invalid"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_116010_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-116-010).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116010_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1,
                          "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116010_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确orderby值")
    @allure.testcase("FT-HTJK-116-011")
    @pytest.mark.parametrize("orderby, result",
                             [('asc', {"code": 1, "msg": ""}),
                              ('desc', {"code": 1, "msg": ""})],
                             ids=["orderby(最小值)", "orderby(最大值)"])
    def test_116011_orderby_correct(self, orderby, result):
        """ Test correct orderby values (最小值、最大值）(FT-HTJK-116-011).
        :param orderby: orderby parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116011_orderby_correct ({}) ....".format(orderby))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "orderby": orderby,
                          "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116011_orderby_correct ({}) ....".format(orderby))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误orderby值")
    @allure.testcase("FT-HTJK-116-012")
    @pytest.mark.parametrize("orderby, result",
                             [(0, {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              (1, {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('a' * 300, {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              (1.0, {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('a', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('中', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('*', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('1a', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('1中', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              ('1*', {"status": 200, "code": 0, "msg": "不是合法的排序字段"}),
                              (' ', {"status": 200, "code": 1, "msg": ""}),
                              ('', {"status": 200, "code": 1, "msg": ""})],
                             ids=["orderby(0)", "orderby(1)", "orderby(超长值)", "orderby(1.0)",
                                  "orderby(字母)", "orderby(中文)", "orderby(特殊字符)", "orderby(数字字母)",
                                  "orderby(数字中文)", "orderby(数字特殊字符)", "orderby(空格)", "orderby(空)", ])
    def test_116012_orderby_wrong(self, orderby, result):
        """ Test wrong orderby values (0、1、超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-116-012).
        :param orderby: orderby parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_116012_orderby_wrong ({}) ....".format(orderby))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "orderby": orderby,
                          "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
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
            self.logger.info(".... End test_116012_orderby_wrong ({}) ....".format(orderby))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-116-013")
    def test_116013_no_token(self):
        """ Test get identity list without token(FT-HTJK-116-013)."""
        self.logger.info(".... Start test_116013_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '未登录或登录已过期' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116013_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-116-014")
    def test_116014_no_member_id(self):
        """ Test get identity list without member_id(FT-HTJK-116-014)."""
        self.logger.info(".... Start test_116014_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"page_index": 1, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116014_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少page_index参数")
    @allure.testcase("FT-HTJK-116-015")
    def test_116015_no_page_index(self):
        """ Test get identity list without page_index(FT-HTJK-116-015)."""
        self.logger.info(".... Start test_116015_no_page_index ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_size": 2, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116015_no_page_index ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少page_size参数")
    @allure.testcase("FT-HTJK-116-016")
    def test_116016_no_page_size(self):
        """ Test get identity list without page_size(FT-HTJK-116-016)."""
        self.logger.info(".... Start test_116016_no_page_size ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116016_no_page_size ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少orderby参数")
    @allure.testcase("FT-HTJK-116-017")
    def test_116017_no_orderby(self):
        """ Test get identity list without orderby(FT-HTJK-116-017)."""
        self.logger.info(".... Start test_116017_no_orderby ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116017_no_orderby ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-116-018")
    def test_116018_no_timestamp(self):
        """ Test get identity list without timestamp(FT-HTJK-116-018)."""
        self.logger.info(".... Start test_116018_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.get(self.URI, params=params, headers=headers)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_116018_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Identity_GetList.py'])
    pytest.main(['-s', 'test_APP_Identity_GetList.py::TestGetIdentityList::test_116001_relatives_2page_1index'])
