#!/usr/bin/env python3
# -*-coding:utf-8-*-

import datetime
from datetime import timedelta
import random
import pytest
import allure

from utils.LogTool import Logger
from utils.ConfigParse import ConfigParse
from utils.HTTPClient import *
from utils.HTTPClient import HTTPClient
from utils.MysqlClient import MysqlClient
from utils.IFFunctions import *


@pytest.mark.H5
@allure.feature("H5-获取商家内容的整体数据")
class TestProvidersCatecontent(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'H5ProvidersCatecontent')
                allure.attach("uri", str(cls.URI))
                cls.logger.info("uri: " + cls.URI)
            with allure.step("初始化HTTP客户端。"):
                cls.sv_protocol = cls.config.getItem('server', 'protocol')
                cls.sv_host = cls.config.getItem('server', 'host')
                sv_port = cls.config.getItem('server', 'port')
                baseurl = '{0}://{1}:{2}'.format(cls.sv_protocol, cls.sv_host, sv_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient = HTTPClient(baseurl)

            with allure.step("初始化HTTP h5客户端。"):
                h5_port = cls.config.getItem('h5', 'port')
                baseurl = '{0}://{1}:{2}'.format(cls.sv_protocol, cls.sv_host, h5_port)
                allure.attach("baseurl", str(baseurl))
                cls.logger.info("baseurl: " + baseurl)
                cls.httpclient1 = HTTPClient(baseurl)

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

            with allure.step("teststep: get provider id"):
                provider_name = cls.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.provider_id = select_result[0][0]

            with allure.step("teststep: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", cls.provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.spu_id = select_result[0][0]

            with allure.step("teststep: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", cls.spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                cls.logger.info("")
                cls.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = cls.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                cls.logger.info("query result: {0}".format(select_result))
                cls.sku_id = select_result[0][0]
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

    @allure.severity("block")
    @allure.story("登录后获取数据")
    @allure.testcase("FT-HTJK-206-001")
    def test_206001_catecontent_with_login(self):
        """ Test catecontent with login. """
        self.logger.info(".... Start test_206001_catecontent_with_login ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
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
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: h5 get info"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("连接H5主页"):
                    r_homeindex = h5_home_index(httpclient1, self.member_id, self.token, self.logger)
                    allure.attach("homeindex", str(r_homeindex))
                    self.logger.info("homeindex: " + str(r_homeindex))
                    assert not r_homeindex
                with allure.step("获取商家数据"):
                    r_cateresult = h5_providers_catecontent(httpclient1, self.provider_id, self.logger)
                    allure.attach("cate result", str(r_cateresult))
                    self.logger.info("cate result: " + str(r_cateresult))
                    assert r_cateresult

            with allure.step("teststep3: get provider content category"):
                table = "bus_provider_content_category"
                condition = ("provider_id", self.provider_id)
                allure.attach("table name and condition", "{0}, {1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                category_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(category_result))
                self.logger.info("query result: {0}".format(category_result))

            with allure.step("teststep4: get provider content"):
                table = "bus_provider_content"
                condition = ("provider_id", self.provider_id)
                allure.attach("table name and condition", "{0}, {1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                content_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(content_result))
                self.logger.info("query result: {0}".format(content_result))

            with allure.step("teststep5: compare content category"):
                categorys = []
                contents = []
                for catecontent in r_cateresult['CateContentList']:
                    categorys.append(catecontent['CateModel'])
                    contents.extend(catecontent['ContentList'])
                allure.attach("categorys", str(categorys))
                allure.attach("contents", str(contents))
                self.logger.info("categorys: {0}".format(categorys))
                self.logger.info("contents: {0}".format(contents))
                assert len(category_result) == len(categorys)
                for database_item, if_item in zip(category_result, categorys):
                    assert database_item[0] == int(if_item['CateId'])
                    assert database_item[2] == if_item['CateName']
                assert len(content_result) == len(contents)
                for database_item, if_item in zip(content_result, contents):
                    assert database_item[0] == int(if_item['ContentId'])
                    assert database_item[3] == if_item['ContentTitle']
                    assert database_item[2] == int(if_item['CateId'])

            with allure.step("teststep6: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_206001_catecontent_with_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("未登录获取数据")
    @allure.testcase("FT-HTJK-206-002")
    def test_206002_catecontent_without_login(self):
        """ Test catecontent without login. """
        self.logger.info(".... Start test_206002_catecontent_without_login ....")
        try:
            with allure.step("teststep1: user login."):
                json = {"code_type": 2, "client_type": 1, "client_version": "v1", "device_token": "12345678901" * 4,
                        "imei": "460011234567890", "phone": "13511229000", "sms_code": "123456",
                        "timestamp": get_timestamp()}
                allure.attach("register params value", str(json))
                self.logger.info("register params: {0}".format(json))
                register_result = make_login(self.httpclient, json['code_type'], json['client_type'], json['client_version'],
                    json['device_token'], json['imei'], json['phone'], json['sms_code'], json['timestamp'], self.logger)
                allure.attach("register result", str(register_result))
                self.logger.info("register result: {0}".format(register_result))
                self.token = register_result['token']
                self.member_id = register_result['user_info']['member_id']
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)

            with allure.step("teststep2: h5 get info"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("获取商家数据"):
                    r_cateresult = h5_providers_catecontent(httpclient1, self.provider_id, self.logger)
                    allure.attach("cate result", str(r_cateresult))
                    self.logger.info("cate result: " + str(r_cateresult))
                    assert r_cateresult

            with allure.step("teststep3: user logout."):
                logout_result = logout(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("logout result", str(logout_result))
                self.logger.info("logout result: {0}".format(logout_result))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_206002_catecontent_without_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("用户未登录获取数据")
    @allure.testcase("FT-HTJK-206-003")
    def test_206003_catecontent_without_user_login(self):
        """ Test catecontent without user login. """
        self.logger.info(".... Start test_206003_catecontent_without_user_login ....")
        try:
            with allure.step("teststep1: h5 get info"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("获取商家数据"):
                    r_cateresult = h5_providers_catecontent(httpclient1, self.provider_id, self.logger)
                    allure.attach("cate result", str(r_cateresult))
                    self.logger.info("cate result: " + str(r_cateresult))
                    assert r_cateresult
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_206003_catecontent_without_user_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误providerId值")
    @allure.testcase("FT-HTJK-206-004")
    @pytest.mark.parametrize("providerId, result",
                             [('1' * 256, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (1.5, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('*', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1a', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('1中', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('%1%', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (' ', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              ('', {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (11111, {"status": 200, "code": 1, "msg": "成功"}),
                              (0, {"status": 200, "code": 99, "msg": "参数异常"}),
                              (-1, {"status": 200, "code": 99, "msg": "参数异常"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["providerId(超长值)", "providerId(小数)", "providerId(英文)", "providerId(中文)",
                                  "providerId(特殊字符)", "providerId(数字英文)", "providerId(数字中文)",
                                  "providerId(数字特殊字符)", "providerId(空格)", "providerId(空)",
                                  "providerId(1)", "providerId(0)", "providerId(-1)", "providerId(超大)",
                                  "providerId(超小)"])
    def test_206004_catecontent_providerid_wrong(self, providerId, result):
        """ Test wrong providerId values (FT-HTJK-206-004).
        :param providerId: providerId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_206004_catecontent_providerid_wrong ({}) ....".format(providerId))
        try:
            with allure.step("teststep1: get parameters."):
                data = {"providerId": providerId}
                allure.attach("params value", "{0}".format(data))
                self.logger.info("data: {0}".format(data))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient1.get(uri=self.URI, params=data)
                allure.attach("request.headers", str(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                if rsp.status_code == 200:
                    rsp_content = rsp.json()
                else:
                    rsp_content = rsp.text

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    if 'code' in rsp_content.keys():
                        assert rsp_content["code"] == result['code']
                        if rsp_content["code"] == 1:
                            assert not rsp_content["result"]['CateContentList']
                            assert rsp_content['success']
                    else:
                        assert rsp_content["status"] == result['code']
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert result['msg'] in rsp.text
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_206004_catecontent_providerid_wrong ({}) ....".format(providerId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少providerId参数")
    @allure.testcase("FT-HTJK-206-005")
    def test_206005_catecontent_without_providerid(self):
        """ Test catecontent without providerId. """
        self.logger.info(".... Start test_206005_catecontent_without_providerid ....")
        try:
            with allure.step("teststep1: get parameters."):
                data = {}
                allure.attach("params value", "{0}".format(data))
                self.logger.info("data: {0}".format(data))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient1.get(uri=self.URI, params=data)
                allure.attach("request.headers", str(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 99
                assert '参数异常' in rsp_content["message"]
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_206005_catecontent_without_providerid ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_H5_Providers_Catecontent.py::TestProvidersCatecontent::test_206005_catecontent_without_providerid'])
    pytest.main(['-s', 'test_H5_Providers_Catecontent.py'])
