#!/usr/bin/env python3
# -*-coding:utf-8-*-

import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *


@allure.feature("APP-获取服务单列表")
class TestCetServiceOrderList(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'GetMyServiceOrderList')
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
                        "imei": "460011234567890", "phone": "13511222251", "sms_code": "123456",
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

            with allure.step("teststep: identity user."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result = user_identity(cls.httpclient, cls.member_id, 'fore2.jpg', 'back2.jpg', 'face2.jpg',
                                                get_timestamp(), cls.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                cls.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep: identity relative."):
                headers = {"authorization": cls.token}
                cls.httpclient.update_header(headers)
                identity_result1 = identity_other(cls.httpclient, cls.member_id, 'kuli1', 'relate_face.jpg',
                                                  'relate_com.jpg',
                                                  get_timestamp(), cls.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                cls.logger.info("identity relative result: {0}".format(identity_result1))

            with allure.step("teststep: get business token."):
                cls.httpclient.update_header({"authorization": cls.token})
                business_result = h5_get_business_token(cls.httpclient, cls.member_id, get_timestamp(), cls.logger)
                allure.attach("business token", str(business_result))
                cls.logger.info("business token: {}".format(business_result))
                business_token = business_result['business_token']

            with allure.step("teststep: get business system id and code"):
                table = 'bus_system'
                condition = ("system_name", '公司类门禁业务系统')
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.system_id = select_result[0][0]
                cls.system_code = select_result[0][2]

            with allure.step("teststep: get devices id"):
                table = 'bus_device'
                condition = ("system_id", cls.system_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.devices_ids = []
                for device in select_result:
                    cls.devices_ids.append(device[0])

            with allure.step("teststep: get features id by user info."):
                user_info = bs_get_user_info(cls.httpclient, cls.system_id, cls.member_id, business_token,
                                             get_timestamp(), cls.logger)
                allure.attach("features data list", "{0}".format(user_info))
                cls.logger.info("features data list: {0}".format(user_info))
                cls.features_ids = []
                for item in user_info['features_info']:
                    cls.features_ids.append(item['features_id'])

            with allure.step("teststep: create service orders"):
                cls.service_orders = []
                for features_id in cls.features_ids:
                    order_result = h5_create_service_order(cls.httpclient, cls.system_id, str(random.randint(1000, 100000)), cls.member_id,
                                        cls.system_code, features_id, cls.devices_ids, 3, get_timestamp(), 9999999999, 10, 'testunit',
                                        'dept1', get_timestamp(), cls.logger)
                    cls.service_orders.append(order_result['service_order_id'])
                allure.attach("order list", str(cls.service_orders))
                cls.logger.info("order list: {0}".format(cls.service_orders))
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
        with allure.step("delete service order records"):
            table = 'bus_service_order'
            condition = ("member_id", cls.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            cls.logger.info("")
            cls.logger.info("table: {0}, condition: {1}".format(table, condition))
            delete_result = cls.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            cls.logger.info("delete result: {0}".format(delete_result))
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("blocker")
    @allure.story("获取第1页")
    @allure.testcase("FT-HTJK-119-001")
    def test_119001_get_0index_of_2page(self):
        """ Test get service order list 0 index of 2 pages(FT-HTJK-119-001)."""
        self.logger.info(".... Start test_119001_get_0index_of_2page ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 1, "state": 3, "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert len(rsp_content['result']['data']) == 1
                assert rsp_content['result']['page']['page_index'] == 0
                assert rsp_content['result']['page']['page_size'] == 1
                assert rsp_content['result']['page']['has_next_page']
                assert not rsp_content['result']['page']['has_previous_page']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119001_get_0index_of_2page ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("获取第2页")
    @allure.testcase("FT-HTJK-119-002")
    def test_119002_get_1index_of_2page(self):
        """ Test get service order list 1 index of 2 pages(FT-HTJK-119-002)."""
        self.logger.info(".... Start test_119002_get_1index_of_2page ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert len(rsp_content['result']['data']) == 1
                assert rsp_content['result']['page']['page_index'] == 1
                assert rsp_content['result']['page']['page_size'] == 1
                assert not rsp_content['result']['page']['has_next_page']
                assert rsp_content['result']['page']['has_previous_page']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119002_get_1index_of_2page ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-119-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 0, "msg": "授权非法"}), ('1.0', {"code": 0, "msg": "授权非法"}),
                              ('*', {"code": 0, "msg": "授权非法"}), ('1*', {"code": 0, "msg": "授权非法"}),
                              ('', {"code": 0, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_119003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-119-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119003_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 1, "page_size": 1, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
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
            self.logger.info(".... End test_119003_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-119-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (1, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (-1, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (1.5, {"status": 400, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(0)", "member_id(最小值)", "member_id(最大值)", "member_id(-1)",
                                  "member_id(小数)",
                                  "member_id(超大)", "member_id(字母)", "member_id(中文)", "member_id(特殊字符)",
                                  "member_id(数字字母)",
                                  "member_id(数字中文)", "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)"])
    def test_119004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-119-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119004_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": member_id, "page_index": 1, "page_size": 1, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119004_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确page_index值")
    @allure.testcase("FT-HTJK-119-005")
    @pytest.mark.parametrize("page_index, result",
                             [(0, {"code": 1, "msg": ""}), (1, {"code": 1, "msg": ""}),
                              (2147483647, {"code": 1, "msg": ""})],
                             ids=["page_index(0)", "page_index(1)", "page_index(2147483647)"])
    def test_119005_page_index_correct(self, page_index, result):
        """ Test correct page_index values (0/1/2147483647）(FT-HTJK-119-005).
        :param page_index: page_index parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119005_page_index_correct ({}) ....".format(page_index))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": page_index, "page_size": 1, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
            self.logger.info(".... End test_119005_page_index_correct ({}) ....".format(page_index))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误page_index值")
    @allure.testcase("FT-HTJK-119-006")
    @pytest.mark.parametrize("page_index, result",
                             [(-1, {"status": 200, "code": 0, "msg": "page_index值非法"}),
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
    def test_119006_page_index_wrong(self, page_index, result):
        """ Test wrong page_index values (-1、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-119-006).
        :param page_index: page_index parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119006_page_index_wrong ({}) ....".format(page_index))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": page_index, "page_size": 1, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119006_page_index_wrong ({}) ....".format(page_index))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确page_size值")
    @allure.testcase("FT-HTJK-119-007")
    @pytest.mark.parametrize("page_size, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2147483647, {"status": 200, "code": 1, "msg": ""})],
                             ids=["page_size(最小值)", "page_size(最大值)"])
    def test_119007_page_size_correct(self, page_size, result):
        """ Test correct page_size values (最小值,最大值）(FT-HTJK-119-007).
        :param page_size: page_size parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119007_page_size_correct ({}) ....".format(page_size))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": page_size, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
            self.logger.info(".... End test_119007_page_size_correct ({}) ....".format(page_size))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误page_size值")
    @allure.testcase("FT-HTJK-119-008")
    @pytest.mark.parametrize("page_size, result",
                             [(-1, {"status": 200, "code": 0, "msg": "page_size值非法"}),
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
    def test_119008_page_size_wrong(self, page_size, result):
        """ Test wrong page_size values (-1、0、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-119-008).
        :param page_size: page_size parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119008_page_size_wrong ({}) ....".format(page_size))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": page_size, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119008_page_size_wrong ({}) ....".format(page_size))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确state值")
    @allure.testcase("FT-HTJK-119-009")
    @pytest.mark.parametrize("state, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2, {"status": 200, "code": 1, "msg": ""}),
                              (3, {"status": 200, "code": 1, "msg": ""})],
                             ids=["state(1)", "state(2)", "state(3)"])
    def test_119009_state_correct(self, state, result):
        """ Test correct state values (1/2/3）(FT-HTJK-119-009).
        :param state: state parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119009_state_correct ({}) ....".format(state))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 1, "state": state,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
                if state == 2:
                    assert not rsp_content['result']['data']
                else:
                    assert rsp_content['result']['data']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119009_state_correct ({}) ....".format(state))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误state值")
    @allure.testcase("FT-HTJK-119-010")
    @pytest.mark.parametrize("state, result",
                             [(-1, {"status": 200, "code": 0, "msg": "state值非法"}),
                              (0, {"status": 200, "code": 0, "msg": "state值非法"}),
                              (4, {"status": 200, "code": 0, "msg": "state值非法"}),
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
                             ids=["state(-1)", "state(0)", "state(4)",
                                  "state(-2147483649)", "state(2147483648)", "state(小数)",
                                  "state(字母)", "state(中文)", "state(特殊字符)",
                                  "state(数字字母)", "state(数字中文)",
                                  "state(数字特殊字符)", "state(空格)", "state(空)"])
    def test_119010_state_wrong(self, state, result):
        """ Test wrong state values (-1、0、-2147483649、2147483648、1.0、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-119-010).
        :param state: state parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119010_state_wrong ({}) ....".format(state))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 1, "state": state,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119010_state_wrong ({}) ....".format(state))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确orderby值")
    @allure.testcase("FT-HTJK-119-011")
    @pytest.mark.parametrize("orderby, result",
                             [('features_id', {"code": 1, "msg": ""}),
                              ('features_id desc', {"code": 1, "msg": ""}),
                              (' ', {"code": 1, "msg": ""}),
                              ('', {"code": 1, "msg": ""})],
                             ids=["orderby(最小值)", "orderby(最大值)", "orderby(空格)", "orderby(空)"])
    def test_119011_orderby_correct(self, orderby, result):
        """ Test correct orderby values (最小值、最大值）(FT-HTJK-119-011).
        :param orderby: orderby parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119011_orderby_correct ({}) ....".format(orderby))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3, "orderby": orderby,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
            self.logger.info(".... End test_119011_orderby_correct ({}) ....".format(orderby))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误orderby值")
    @allure.testcase("FT-HTJK-119-012")
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
                              ('1*', {"status": 200, "code": 0, "msg": "不是合法的排序字段"})],
                             ids=["orderby(0)", "orderby(1)", "orderby(超长值)", "orderby(1.0)",
                                  "orderby(字母)", "orderby(中文)", "orderby(特殊字符)", "orderby(数字字母)",
                                  "orderby(数字中文)", "orderby(数字特殊字符)"])
    def test_119012_orderby_wrong(self, orderby, result):
        """ Test wrong orderby values (0、1、超长值、1.0、字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-119-012).
        :param orderby: orderby parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119012_orderby_wrong ({}) ....".format(orderby))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3, "orderby": orderby,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119012_orderby_wrong ({}) ....".format(orderby))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确search值")
    @allure.testcase("FT-HTJK-119-013")
    @pytest.mark.parametrize("search, result",
                             [('k', {"code": 1, "msg": ""}),
                              ('kuli1', {"code": 1, "msg": ""})],
                             ids=["search(部分值)", "search(完整值)"])
    def test_119013_search_correct(self, search, result):
        """ Test correct search values (最小值、最大值）(FT-HTJK-119-013).
        :param search: search parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119013_search_correct ({}) ....".format(search))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3, "search": search,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
            self.logger.info(".... End test_119013_search_correct ({}) ....".format(search))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误search值")
    @allure.testcase("FT-HTJK-119-014")
    @pytest.mark.parametrize("search, result",
                             [(1.5, {"status": 200, "code": 0, "msg": ""}),
                              ('1*'*100, {"status": 200, "code": 0, "msg": ""})],
                             ids=["search(小数)", "search(超长值)"])
    def test_119014_search_wrong(self, search, result):
        """ Test wrong orderby values (超长值、1.0）(FT-HTJK-119-014).
        :param search: search parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119014_search_wrong ({}) ....".format(search))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3, "search": search,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119014_search_wrong ({}) ....".format(search))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-119-015")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 1000, {"code": 1, "msg": ""}),
                              (get_timestamp() + 1000, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_119015_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-119-015).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119015_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": timestamp}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
            self.logger.info(".... End test_119015_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-119-016")
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
    def test_119016_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-119-016).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_119016_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": timestamp}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
            self.logger.info(".... End test_119016_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-119-017")
    def test_119017_no_token(self):
        """ Test get service order list without token(FT-HTJK-119-017)."""
        self.logger.info(".... Start test_119017_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": None})
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
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
            self.logger.info(".... End test_119017_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-119-018")
    def test_119018_no_member_id(self):
        """ Test get service order list without member_id(FT-HTJK-119-018)."""
        self.logger.info(".... Start test_119018_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119018_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少page_index参数")
    @allure.testcase("FT-HTJK-119-019")
    def test_119019_no_page_index(self):
        """ Test get service order list without page_index(FT-HTJK-119-019)."""
        self.logger.info(".... Start test_119019_no_page_index ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_size": 10, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119019_no_page_index ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少page_size参数")
    @allure.testcase("FT-HTJK-119-020")
    def test_119020_no_page_size(self):
        """ Test get service order list without page_size(FT-HTJK-119-020)."""
        self.logger.info(".... Start test_119020_no_page_size ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119020_no_page_size ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少state参数")
    @allure.testcase("FT-HTJK-119-021")
    def test_119021_no_state(self):
        """ Test get service order list without state(FT-HTJK-119-021)."""
        self.logger.info(".... Start test_119021_no_state ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 0
                assert 'state值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119021_no_state ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少orderby参数")
    @allure.testcase("FT-HTJK-119-022")
    def test_119022_no_orderby(self):
        """ Test get service order list without orderby(FT-HTJK-119-022)."""
        self.logger.info(".... Start test_119022_no_orderby ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119022_no_orderby ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少search参数")
    @allure.testcase("FT-HTJK-119-023")
    def test_119023_no_search(self):
        """ Test get service order list without search(FT-HTJK-119-023)."""
        self.logger.info(".... Start test_119023_no_search ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3,
                          "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119023_no_search ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-119-024")
    def test_119024_no_timestamp(self):
        """ Test get service order list without timestamp(FT-HTJK-119-024)."""
        self.logger.info(".... Start test_119024_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "page_index": 0, "page_size": 10, "state": 3}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                self.httpclient.update_header({"authorization": self.token})
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 0
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_119024_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Get_Service_Order_List.py'])
    pytest.main(['-s', 'test_APP_Get_Service_Order_List.py::TestCetServiceOrderList::test_119001_get_0index_of_2page'])
