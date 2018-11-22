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


@allure.feature("APP-删除关联人")
class TestDeleteRelatives(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'RemoveIdentityOther')
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
                        "imei": "460011234567890", "phone": "13511222191", "sms_code": "123456",
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
                assert identity_result
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
    @allure.story("删除关联人成功")
    @allure.testcase("FT-HTJK-118-001")
    def test_118001_relatives_delete_correct(self):
        """ Test delete relatives with correct parameters(FT-HTJK-118-001)."""
        self.logger.info(".... Start test_118001_relatives_delete_correct ....")
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

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(), logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert result_list

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id,"timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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
                assert '删除成功' in  rsp_content['message']

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert not match_list
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
            self.logger.info(".... End test_118001_relatives_delete_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-118-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 0, "msg": "授权非法"}), ('1.0', {"code": 0, "msg": "授权非法"}),
                              ('*', {"code": 0, "msg": "授权非法"}), ('1*', {"code": 0, "msg": "授权非法"}),
                              ('', {"code": 0, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_118002_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-118-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_118002_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert result_list

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118002_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-118-003")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (1.0, {"status": 200, "code": 0, "msg": "授权非法"}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": "授权非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(最小值)","member_id(最大值)","member_id(小数)",
                                  "member_id(中文)", "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_118003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-118-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_118003_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert result_list

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": member_id, "features_id": features_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118003_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误features_id值")
    @allure.testcase("FT-HTJK-118-004")
    @pytest.mark.parametrize("features_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 0, "msg": ""}),
                              (1, {"status": 200, "code": 0, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": ""}),
                              (1.0, {"status": 200, "code": 0, "msg": ""}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""})],
                             ids=["features_id(超长值)", "features_id(0)", "features_id(最小值)", "features_id(最大值)",
                                  "features_id(小数)", "features_id(超大)", "features_id(超小)",
                                  "features_id(中文)", "features_id(特殊字符)", "features_id(数字中文)",
                                  "features_id(数字特殊字符)", "features_id(空格)", "features_id(空)"])
    def test_118004_features_id_wrong(self, features_id, result):
        """ Test wrong features_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-118-004).
        :param features_id: features_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_118004_features_id_wrong ({}) ....".format(features_id))
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert result_list

            with allure.step("teststep2: get parameters."):
                json = {"member_id": self.member_id, "features_id": features_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == result_list[0]['features_id'], select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118004_features_id_wrong ({}) ....".format(features_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-118-005")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 10000, {"code": 1, "msg": "删除成功"}),
                              (get_timestamp() + 1000, {"code": 1, "msg": "删除成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_118005_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-118-005).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_118005_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert result_list

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert not match_list
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
            self.logger.info(".... End test_118005_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-118-006")
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
    def test_118006_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-118-006).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_118006_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert len(result_list) == 1

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id, "timestamp": timestamp}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            with allure.step("delete database records"):
                table = 'mem_features'
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                self.logger.info(result_list)
                for member in result_list:
                    condition = ("features_id", member['features_id'])
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    delete_result = self.mysql.execute_delete_condition(table, condition)
                    allure.attach("delete result", str(delete_result))
                    self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_118006_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-118-007")
    def test_118007_no_token(self):
        """ Test delete relatives without token(FT-HTJK-118-007)."""
        self.logger.info(".... Start test_118007_no_token ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert len(result_list) == 1

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id, "timestamp": get_timestamp()}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, json=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

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

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118007_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-118-008")
    def test_118008_no_member_id(self):
        """ Test delete relatives without member_id(FT-HTJK-118-008)."""
        self.logger.info(".... Start test_118008_no_member_id ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert len(result_list) == 1

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"features_id": features_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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
                assert rsp_content["code"] == 0
                assert '授权非法' in rsp_content['message']

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118008_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少features_id参数")
    @allure.testcase("FT-HTJK-118-009")
    def test_118009_no_features_id(self):
        """ Test delete relatives without features_id(FT-HTJK-118-009)."""
        self.logger.info(".... Start test_118009_no_features_id ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert len(result_list) == 1

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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
                assert rsp_content["code"] == 0
                assert '特征不存在' in rsp_content['message']

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118009_no_features_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-118-010")
    def test_118010_no_timestamp(self):
        """ Test delete relatives without timestamp(FT-HTJK-118-010)."""
        self.logger.info(".... Start test_118010_no_timestamp ....")
        try:
            with allure.step("teststep1: identity other."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity_result", "{0}".format(identity_result1))
                self.logger.info("identity_result: {0}".format(identity_result1))

            with allure.step("teststep2: get relatives."):
                result_list = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                      logger=self.logger)
                allure.attach("result_list value", "{0}".format(result_list))
                self.logger.info("result_list: {0}".format(result_list))
                assert len(result_list) == 1

            with allure.step("teststep2: get parameters."):
                features_id = result_list[0]['features_id']
                json = {"member_id": self.member_id, "features_id": features_id}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep3: requests http post."):
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
                assert rsp_content["code"] == 0
                assert 'timestamp不能为空' in rsp_content['message']

            with allure.step("teststep6: query database records"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 2
                match_list = list(filter(lambda x: x[0] == features_id, select_result))
                self.logger.info("match list: {}".format(match_list))
                assert match_list
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
            self.logger.info(".... End test_118010_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Identity_Relatives_Delete.py'])
    pytest.main(['-s', 'test_APP_Identity_Relatives_Delete.py::TestDeleteRelatives::test_118001_relatives_delete_correct'])
