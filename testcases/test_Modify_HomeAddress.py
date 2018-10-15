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


@allure.feature("修改家庭地址")
class TestModifyHomeAddress(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'ModifyHomeAddress')
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
                        "imei": "460011234567890", "phone": "13511222131", "sms_code": "123456",
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
        if hasattr(cls, 'httpclient'):
            cls.httpclient.close()
        if hasattr(cls, 'mysql'):
            cls.mysql.close()
        cls.logger.info("*** End teardown class ***")
        cls.logger.info("")

    @allure.severity("critical")
    @allure.story("正确修改家庭地址")
    @allure.testcase("FT-HTJK-110-001")
    def test_110001_modify_home_address_correct(self):
        """ Test modify home address by correct parameters(FT-HTJK-110-001)."""
        self.logger.info(".... Start test_110001_modify_home_address_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert '修改家庭地址成功' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['province'] == json['province']
                assert info['city'] == json['city']
                assert info['district'] == json['district']
                assert info['address'] == json['address']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110001_modify_home_address_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-110-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 0, "msg": "授权非法"}), ('1.0', {"code": 0, "msg": "授权非法"}),
                              ('*', {"code": 0, "msg": "授权非法"}), ('1*', {"code": 0, "msg": "授权非法"}),
                              ('', {"code": 0, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_110002_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-110-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110002_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110002_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-110-003")
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
    def test_110003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-110-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110003_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110003_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确province值")
    @allure.testcase("FT-HTJK-110-004")
    @pytest.mark.parametrize("province, result",
                             [('1' * 50, {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1.0', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('abc', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('*', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1*', {"code": 1, "msg": "修改家庭地址成功"})],
                             ids=["province(超长值)", "province(小数)", "province(字母)", "province(中文)",
                                  "province(特殊字符)", "province(数字中文)", "province(数字特殊字符)"])
    def test_110004_province_correct(self, province, result):
        """ Test correct province values (超长值、1.0、字母、中文、特殊字符、数字中文、数字特殊字符）(FT-HTJK-110-004).
        :param province: province parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110004_province_correct ({}) ....".format(province))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": province, "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['province'] == province
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110004_province_correct ({}) ....".format(province))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误province值")
    @allure.testcase("FT-HTJK-110-005")
    @pytest.mark.parametrize("province, result",
                             [('1' * 100, {"code": 0, "msg": "province值非法"}),
                              (' ', {"code": 0, "msg": "province值非法"}),
                              ('', {"code": 0, "msg": "province值非法"})],
                             ids=["province(超长值)", "province(空格)", "province(空)"])
    def test_110005_province_wrong(self, province, result):
        """ Test wrong province values (超长值、空格、空）(FT-HTJK-110-005).
        :param province: province parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110005_province_wrong ({}) ....".format(province))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": province, "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110005_province_wrong ({}) ....".format(province))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确city值")
    @allure.testcase("FT-HTJK-110-006")
    @pytest.mark.parametrize("city, result",
                             [('1' * 50, {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1.0', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('abc', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('*', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1*', {"code": 1, "msg": "修改家庭地址成功"})],
                             ids=["city(超长值)", "city(小数)", "city(字母)", "city(中文)",
                                  "city(特殊字符)", "city(数字中文)", "city(数字特殊字符)"])
    def test_110006_city_correct(self, city, result):
        """ Test correct city values (超长值、1.0、字母、中文、特殊字符、数字中文、数字特殊字符）(FT-HTJK-110-006).
        :param city: city parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110006_city_correct ({}) ....".format(city))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": city, "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['city'] == city
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110006_city_correct ({}) ....".format(city))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误city值")
    @allure.testcase("FT-HTJK-110-007")
    @pytest.mark.parametrize("city, result",
                             [('1' * 100, {"code": 0, "msg": "city值非法"}),
                              (' ', {"code": 0, "msg": "city值非法"}),
                              ('', {"code": 0, "msg": "city值非法"})],
                             ids=["city(超长值)", "city(空格)", "city(空)"])
    def test_110007_city_wrong(self, city, result):
        """ Test wrong city values (超长值、空格、空）(FT-HTJK-110-007).
        :param city: city parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110007_city_wrong ({}) ....".format(city))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": city, "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110007_city_wrong ({}) ....".format(city))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确district值")
    @allure.testcase("FT-HTJK-110-008")
    @pytest.mark.parametrize("district, result",
                             [('1' * 50, {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1.0', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('abc', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('*', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1*', {"code": 1, "msg": "修改家庭地址成功"})],
                             ids=["district(超长值)", "district(小数)", "district(字母)", "district(中文)",
                                  "district(特殊字符)", "district(数字中文)", "district(数字特殊字符)"])
    def test_110008_district_correct(self, district, result):
        """ Test correct district values (超长值、1.0、字母、中文、特殊字符、数字中文、数字特殊字符）(FT-HTJK-110-008).
        :param district: district parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110008_district_correct ({}) ....".format(district))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": district,
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['district'] == district
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110008_district_correct ({}) ....".format(district))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误district值")
    @allure.testcase("FT-HTJK-110-009")
    @pytest.mark.parametrize("district, result",
                             [('1' * 100, {"code": 0, "msg": "district值非法"}),
                              (' ', {"code": 0, "msg": "district值非法"}),
                              ('', {"code": 0, "msg": "district值非法"})],
                             ids=["city(超长值)", "city(空格)", "city(空)"])
    def test_110009_district_wrong(self, district, result):
        """ Test wrong city values (超长值、空格、空）(FT-HTJK-110-009).
        :param district: district parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110009_district_wrong ({}) ....".format(district))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": district,
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110009_district_wrong ({}) ....".format(district))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确address值")
    @allure.testcase("FT-HTJK-110-010")
    @pytest.mark.parametrize("address, result",
                             [('1' * 50, {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1.0', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('abc', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('*', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1中', {"code": 1, "msg": "修改家庭地址成功"}),
                              ('1*', {"code": 1, "msg": "修改家庭地址成功"})],
                             ids=["address(超长值)", "address(小数)", "address(字母)", "address(中文)",
                                  "address(特殊字符)", "address(数字中文)", "address(数字特殊字符)"])
    def test_110010_address_correct(self, address, result):
        """ Test correct address values (超长值、1.0、字母、中文、特殊字符、数字中文、数字特殊字符）(FT-HTJK-110-010).
        :param address: address parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110010_address_correct ({}) ....".format(address))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": address, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['address'] == address
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110010_address_correct ({}) ....".format(address))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误address值")
    @allure.testcase("FT-HTJK-110-011")
    @pytest.mark.parametrize("address, result",
                             [('1' * 100, {"code": 0, "msg": "address值非法"}),
                              (' ', {"code": 0, "msg": "address值非法"}),
                              ('', {"code": 0, "msg": "address值非法"})],
                             ids=["address(超长值)", "address(空格)", "address(空)"])
    def test_110011_address_wrong(self, address, result):
        """ Test wrong address values (超长值、空格、空）(FT-HTJK-110-011).
        :param address: address parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110011_address_wrong ({}) ....".format(address))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": address, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110011_address_wrong ({}) ....".format(address))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-110-012")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 10000, {"code": 1, "msg": "修改家庭地址成功"}),
                              (get_timestamp(), {"code": 1, "msg": "修改家庭地址成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_110012_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-110-012).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110012_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110012_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-110-013")
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
    def test_110013_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-110-013).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_110013_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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
                    assert result['msg'] in rsp_content["message"]
                else:
                    assert rsp_content

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110013_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-110-014")
    def test_110014_no_token(self):
        """ Test modify home address without token(FT-HTJK-110-014)."""
        self.logger.info(".... Start test_110014_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 401
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '未登录或登录已过期' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110014_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-110-015")
    def test_110015_no_member_id(self):
        """ Test modify home address without member_id(FT-HTJK-110-015)."""
        self.logger.info(".... Start test_110015_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"province": '广东省', "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110015_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少province参数")
    @allure.testcase("FT-HTJK-110-016")
    def test_110016_no_province(self):
        """ Test modify home address without province(FT-HTJK-110-016)."""
        self.logger.info(".... Start test_110016_no_province ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "city": '广州市', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'province值非法' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110016_no_province ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少city参数")
    @allure.testcase("FT-HTJK-110-017")
    def test_110017_no_city(self):
        """ Test modify home address without city(FT-HTJK-110-017)."""
        self.logger.info(".... Start test_110017_no_city ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "district": '番禺区',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'city值非法' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110017_no_city ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少district参数")
    @allure.testcase("FT-HTJK-110-018")
    def test_110018_no_district(self):
        """ Test modify home address without district(FT-HTJK-110-018)."""
        self.logger.info(".... Start test_110018_no_district ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市',
                        "address": '北大街2号', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'district值非法' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110018_no_district ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少address参数")
    @allure.testcase("FT-HTJK-110-019")
    def test_110019_no_address(self):
        """ Test modify home address without address(FT-HTJK-110-019)."""
        self.logger.info(".... Start test_110019_no_address ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市',
                        "district": '番禺区', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'address值非法' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110019_no_address ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-110-020")
    def test_110020_no_timestamp(self):
        """ Test modify home address without timestamp(FT-HTJK-110-020)."""
        self.logger.info(".... Start test_110020_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "province": '广东省', "city": '广州市',
                        "district": '番禺区', "address": '北大街2号'}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 0
                assert 'timestamp不能为空' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_110020_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_Modify_HomeAddress.py'])
    # pytest.main(['-s', 'test_Modify_HomeAddress.py::TestModifyHomeAddress::test_110020_no_timestamp'])
