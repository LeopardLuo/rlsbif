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


@allure.feature("业务系统上传照片获得特征ID")
class TestBSGenFeatureId(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'BSGenFeatureId')
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
                        "imei": "460011234567890", "phone": "13511222361", "sms_code": "123456",
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

    @allure.severity("blocker")
    @allure.story("第三方业务系统上传成功")
    @allure.testcase("FT-HTJK-208-001")
    def test_208001_gen_featureid_correct(self):
        """ Test gen feature id by correct parameters(FT-HTJK-208-001)."""
        self.logger.info(".... Start test_208001_gen_featureid_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert not rsp_content['message']
                assert rsp_content['result']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208001_gen_featureid_correct ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("hrst业务系统上传成功")
    @allure.testcase("FT-HTJK-208-002")
    def test_208002_gen_featureid_h5(self):
        """ Test h5 gen feature id by correct parameters(FT-HTJK-208-002)."""
        self.logger.info(".... Start test_208002_gen_featureid_h5 ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert not rsp_content['message']
                assert rsp_content['result']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208002_gen_featureid_h5 ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_id值")
    @allure.testcase("FT-HTJK-208-003")
    @pytest.mark.parametrize("system_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (1, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 202004, "msg": "该业务系统不存在"}),
                              (-1, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (1.0, {"status": 200, "code": 101000, "msg": "system_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              ('a', {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1a', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["system_id(超长值)", "system_id(0)", "system_id(最小值)", "system_id(最大值)", "system_id(-1)",
                                  "system_id(小数)",
                                  "system_id(超大)", "system_id(字母)", "system_id(中文)", "system_id(特殊字符)",
                                  "system_id(数字字母)",
                                  "system_id(数字中文)", "system_id(数字特殊字符)", "system_id(空格)", "system_id(空)"])
    def test_208003_system_id_wrong(self, system_id, result):
        """ Test wrong system_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-208-003).
        :param system_id: system_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208003_system_id_wrong ({}) ....".format(system_id))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208003_system_id_wrong ({}) ....".format(system_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误system_code值")
    @allure.testcase("FT-HTJK-208-004")
    @pytest.mark.parametrize("system_code, result",
                             [('1' * 1001, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (0, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (1, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (-1, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (1.0, {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('a', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('中', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('*', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1a', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1中', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('1*', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              (' ', {"status": 200, "code": 202005, "msg": "授权非法"}),
                              ('', {"status": 200, "code": 202005, "msg": "授权非法"})],
                             ids=["system_code(超长值)", "system_code(0)", "system_code(最小值)", "system_code(-1)",
                                  "system_code(小数)", "system_code(字母)", "system_code(中文)", "system_code(特殊字符)",
                                  "system_code(数字字母)",
                                  "system_code(数字中文)", "system_code(数字特殊字符)", "system_code(空格)", "system_code(空)"])
    def test_208004_system_code_wrong(self, system_code, result):
        """ Test wrong system_code values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-208-004).
        :param system_code: system_code parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208004_system_code_wrong ({}) ....".format(system_code))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208004_system_code_wrong ({}) ....".format(system_code))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-208-005")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 1001, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (1, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (9223372036854775807, {"status": 200, "code": 202007, "msg": "客户特征不存在"}),
                              (-1, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
                              (1.0, {"status": 200, "code": 101001, "msg": "member_id值非法"}),
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
    def test_208005_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、0、最小值、最大值、-1、1.0、超大值、字母、中文、特殊字符、数字字母、
        数字中文、数字特殊字符、空格、空）(FT-HTJK-208-005).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208005_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208005_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确name值")
    @allure.testcase("FT-HTJK-208-006")
    @pytest.mark.parametrize("name, result",
                             [('1234', {"code": 1, "msg": "修改昵称成功"}), ('1' * 10, {"code": 1, "msg": "修改昵称成功"}),
                              ('abcd', {"code": 1, "msg": "修改昵称成功"}), ('中中中中', {"code": 1, "msg": "修改昵称成功"}),
                              ('(*.)', {"code": 1, "msg": "修改昵称成功"}), ('1a*中', {"code": 1, "msg": "修改昵称成功"}),
                              (1.123, {"code": 1, "msg": "修改昵称成功"})],
                             ids=["name(最小长度值)", "name(最大长度值)", "name(字母)",
                                  "name(中文)", "name(特殊字符)", "name(数字字母中文特殊字符)", "name(小数)", ])
    def test_208006_name_correct(self, name, result):
        """ Test correct nickname values (最小长度值、最大长度值、字母、中文、特殊字符、数字字母中文特殊字符、空格、空）(FT-HTJK-208-006).
        :param name: name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208006_name_correct ({}) ....".format(name))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": name,
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208006_name_correct ({}) ....".format(name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误name值")
    @allure.testcase("FT-HTJK-208-007")
    @pytest.mark.parametrize("name, result",
                             [('123', {"code": 0, "msg": ""}), ('1' * 11, {"code": 0, "msg": ""}),
                              ('     ', {"code": 0, "msg": ""}), ('', {"code": 0, "msg": ""})],
                             ids=["name(超短值)", "name(超长值)", "name(空格)", "name(空)"])
    def test_208007_name_wrong(self, name, result):
        """ Test wrong name values (小数、超长值）(FT-HTJK-208-007).
        :param name: name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208007_name_wrong ({}) ....".format(name))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": name,
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208007_name_wrong ({}) ....".format(name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("photo支持的图片类型")
    @allure.testcase("FT-HTJK-208-008")
    @pytest.mark.parametrize("photo, result",
                             [("relate_face.png", {"code": 1, "msg": ""}),
                              ("relate_face.jpg", {"code": 1, "msg": ""}),
                              ("relate_face.jpeg", {"code": 1, "msg": ""}),
                              ("relate_face.tif", {"code": 1, "msg": ""}),
                              ("relate_face.bmp", {"code": 1, "msg": ""}), ],
                             ids=["photo(png)", "photo(jpg)", "photo(jpeg)",
                                  "photo(tif)", "photo(bmp)"])
    def test_208008_photo_type_correct(self, photo, result):
        """ Test correct photo image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-208-008).
        :param photo: photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208008_photo_type_correct ({}) ....".format(photo))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path(photo), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208008_photo_type_correct ({}) ....".format(photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("photo不支持的文件类型")
    @allure.testcase("FT-HTJK-208-009")
    @pytest.mark.parametrize("photo, result",
                             [("relate_face.gif", {"code": 0, "msg": "不合格"}),
                              ("case.xlsx", {"code": 0, "msg": "不合格"}),
                              ("temp.txt", {"code": 0, "msg": "不合格"}),
                              ("hb.mp4", {"code": 0, "msg": "不合格"}),
                              ("fore1.PNG", {"code": 0, "msg": "不通过"}), ],
                             ids=["photo(gif)", "photo(xlsx)", "photo(txt)",
                                  "photo(mp4)", "photo(other)"])
    def test_208009_photo_type_wrong(self, photo, result):
        """ Test wrong photo image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-208-009).
        :param photo: photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208009_photo_type_wrong ({}) ....".format(photo))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path(photo), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208009_photo_type_wrong ({}) ....".format(photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-208-010")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 100, {"code": 1, "msg": ""}),
                              (get_timestamp() + 100, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_208010_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-208-010).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208010_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": timestamp}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208010_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-208-011")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (9223372036854775807, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (0, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (-1, {"status": 200, "code": 101002, "msg": "timestamp值非法"}),
                              (get_timestamp() - 1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (get_timestamp() + 1000, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is invalid"}),
                              (1.5, {"status": 200, "code": 202003, "msg": "timestamp值已过期"}),
                              ('a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "is invalid"}),
                              (' ', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('', {"status": 400, "code": 0, "msg": "is invalid"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(允许超小值)", "timestamp(允许超大值)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_208011_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、允许超小值、允许超大值、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-208-011).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_208011_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"system_id": self.system_id, "member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": timestamp}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                    assert result['msg'] in rsp_content['message']
                else:
                    assert rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208011_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_id参数")
    @allure.testcase("FT-HTJK-208-012")
    def test_208012_no_system_id(self):
        """ Test gen feature id without system_id(FT-HTJK-208-012)."""
        self.logger.info(".... Start test_208012_no_system_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "name": "kuli",
                          "system_code": self.system_code, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208012_no_system_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少system_code参数")
    @allure.testcase("FT-HTJK-208-013")
    def test_208013_no_system_code(self):
        """ Test gen feature id without system_code(FT-HTJK-208-013)."""
        self.logger.info(".... Start test_208013_no_system_code ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "name": "kuli",
                          "system_id": self.system_id, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208013_no_system_code ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少name参数")
    @allure.testcase("FT-HTJK-208-014")
    def test_208014_no_name(self):
        """ Test gen feature id without name(FT-HTJK-208-014)."""
        self.logger.info(".... Start test_208014_no_name ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "system_code": self.system_code,
                          "system_id": self.system_id, "timestamp": get_timestamp()}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208014_no_name ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少photo参数")
    @allure.testcase("FT-HTJK-208-015")
    def test_208015_no_photo(self):
        """ Test gen feature id without photo(FT-HTJK-208-015)."""
        self.logger.info(".... Start test_208015_no_photo ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "system_code": self.system_code, "name": "kuli",
                          "system_id": self.system_id, "timestamp": get_timestamp()}
                files = {"face": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208015_no_photo ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-208-016")
    def test_208016_no_timestamp(self):
        """ Test gen feature id without timestamp(FT-HTJK-208-016)."""
        self.logger.info(".... Start test_208016_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "system_code": self.system_code, "name": "kuli",
                          "system_id": self.system_id}
                files = {"photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http post."):
                rsp = self.httpclient.post(self.URI, data=params, files=files)
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
                assert '' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_208016_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_BS_ServiceOrder_GenFeatureId.py'])
    pytest.main(['-s', 'test_BS_ServiceOrder_GenFeatureId.py::TestBSGenFeatureId::test_208001_gen_featureid_correct'])
