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


@pytest.mark.APP
@allure.feature("APP-临时用户成员添加")
class TestIdentityTemp(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'IdentityTemp')
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
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "12345678901"*4,
                        "imei": "460011234567890", "phone": "13511222271", "sms_code": "123456",
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

    @allure.step("+++ teardown method +++")
    def teardown_method(self, method):
        self.logger.info("")
        self.logger.info("=== Start teardown method ===")
        self.logger.info(method.__name__)
        with allure.step("delete mem_features"):
            table = 'mem_features'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("delele records of table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete mem_member_identity"):
            table = 'mem_member_identity'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("delele records of table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        with allure.step("delete mem_member_identity_other"):
            table = 'mem_member_identity_other'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("delele records of table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("blocker")
    @allure.story("用户成员添加成功")
    @allure.testcase("FT-HTJK-125-001")
    def test_125001_identity_temp_correct(self):
        """ Test identity temp by correct parameters(FT-HTJK-125-001)."""
        self.logger.info(".... Start test_125001_identity_temp_correct ....")
        try:
            with allure.step("teststep1: identity user."):
                with allure.step("teststep: user feature."):
                    headers = {"authorization": self.token}
                    self.httpclient.update_header(headers)
                    identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                     get_timestamp(), self.logger)
                    allure.attach("upload user feature result", "{0}".format(identity_result))
                    self.logger.info("upload user feature result: {0}".format(identity_result))

                with allure.step("teststep: identity user."):
                    headers = {"authorization": self.token}
                    self.httpclient.update_header(headers)
                    identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                    get_timestamp(), self.logger)
                    allure.attach("identity owner result", "{0}".format(identity_result))
                    self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))
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
                assert rsp_content['result']['feature_id']

            # with allure.step("teststep6: query database records"):
            #     table = 'mem_member_identity_other'
            #     condition = ("member_id", self.member_id)
            #     allure.attach("table name and condition", "{0},{1}".format(table, condition))
            #     self.logger.info("")
            #     self.logger.info("table: {0}, condition: {1}".format(table, condition))
            #     select_result = self.mysql.execute_select_condition(table, condition)
            #     allure.attach("query result", str(select_result))
            #     self.logger.info("query result: {0}".format(select_result))
            #     assert len(select_result) == 1
            #     assert select_result[0][2] == params['features_name']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125001_identity_temp_correct ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("用户未认证，添加临时成员失败")
    @allure.testcase("FT-HTJK-125-002")
    def test_125002_identity_temp_without_user(self):
        """ Test identity temp without user identity(FT-HTJK-125-002)."""
        self.logger.info(".... Start test_125002_identity_temp_without_user ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 201401
                assert '请先完成本人的信息采集' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125002_identity_temp_without_user ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-125-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_125003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-125-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125003_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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
            self.logger.info(".... End test_125003_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-125-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 201001, "msg": "授权非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_125004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-125-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125004_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
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
            self.logger.info(".... End test_125004_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确feature_name值")
    @allure.testcase("FT-HTJK-125-005")
    @pytest.mark.parametrize("feature_name, result",
                             [('1', {"code": 1, "msg": ""}), ('1' * 50, {"code": 1, "msg": ""}),
                              ('abcd', {"code": 1, "msg": ""}), ('中中中中', {"code": 1, "msg": ""}),
                              ('(*.)', {"code": 1, "msg": ""}), ('1a*中', {"code": 1, "msg": ""}),
                              (1.123, {"code": 1, "msg": ""})],
                             ids=["feature_name(最小长度值)", "feature_name(最大长度值)", "feature_name(字母)",
                                  "feature_name(中文)", "feature_name(特殊字符)", "feature_name(数字字母中文特殊字符)",
                                  "feature_name(小数)", ])
    def test_125005_feature_name_correct(self, feature_name, result):
        """ Test correct feature_name values (最小长度值、最大长度值、字母、中文、特殊字符、数字字母中文特殊字符、空格、空）(FT-HTJK-125-005).
        :param feature_name: feature_name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125005_feature_name_correct ({}) ....".format(feature_name))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": feature_name, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']['feature_id']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125005_feature_name_correct ({}) ....".format(feature_name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误feature_name值")
    @allure.testcase("FT-HTJK-125-006")
    @pytest.mark.parametrize("feature_name, result",
                             [('1' * 101, {"code": 201903, "msg": "采集失败"}),
                              ('     ', {"code": 201903, "msg": "采集失败"}), ('', {"code": 201903, "msg": "采集失败"})],
                             ids=["feature_name(超长值)", "feature_name(空格)", "feature_name(空)"])
    def test_125006_feature_name_wrong(self, feature_name, result):
        """ Test wrong feature_name values (超长值、空格、空）(FT-HTJK-125-006).
        :param feature_name: feature_name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125006_feature_name_wrong ({}) ....".format(feature_name))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": feature_name, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
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
            self.logger.info(".... End test_125006_feature_name_wrong ({}) ....".format(feature_name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("temp_photo支持的图片类型")
    @allure.testcase("FT-HTJK-125-007")
    @pytest.mark.parametrize("temp_photo, result",
                             [("relate_face.png", {"code": 1, "msg": ""}),
                              ("relate_face.jpg", {"code": 1, "msg": ""}),
                              ("relate_face.jpeg", {"code": 1, "msg": ""}),
                              ("relate_face.tif", {"code": 1, "msg": ""}),
                              ("relate_face.bmp", {"code": 1, "msg": ""}), ],
                             ids=["temp_photo(png)", "temp_photo(jpg)", "temp_photo(jpeg)",
                                  "temp_photo(tif)", "temp_photo(bmp)"])
    def test_125007_temp_photo_type_correct(self, temp_photo, result):
        """ Test correct temp_photo image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-125-007).
        :param temp_photo: temp_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125007_temp_photo_type_correct ({}) ....".format(temp_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path(temp_photo), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 1
                assert not rsp_content['message']
                assert rsp_content['result']['feature_id']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125007_temp_photo_type_correct ({}) ....".format(temp_photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("temp_photo不支持的文件类型")
    @allure.testcase("FT-HTJK-125-008")
    @pytest.mark.parametrize("temp_photo, result",
                             [("relate_face.gif", {"code": 201412, "msg": "照片不合格"}),
                              ("case.xlsx", {"code": 201412, "msg": "照片不合格"}),
                              ("temp.txt", {"code": 201412, "msg": "照片不合格"}),
                              ("hb.mp4", {"code": 201412, "msg": "照片不合格"}),
                              ("dog5.jpg", {"code": 201412, "msg": "照片不合格"}), ],
                             ids=["temp_photo(gif)", "temp_photo(xlsx)", "temp_photo(txt)",
                                  "temp_photo(mp4)", "temp_photo(other)"])
    def test_125008_temp_photo_type_wrong(self, temp_photo, result):
        """ Test wrong temp_photo image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-125-008).
        :param temp_photo: temp_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125008_temp_photo_type_wrong ({}) ....".format(temp_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path(temp_photo), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
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
            self.logger.info(".... End test_125008_temp_photo_type_wrong ({}) ....".format(temp_photo))
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人在合拍照")
    @allure.testcase("FT-HTJK-125-009")
    def test_125009_relatives_in_community(self):
        """ Test relatives in communtity_picture(FT-HTJK-125-009)."""
        self.logger.info(".... Start test_125009_relatives_in_community ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_com.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                print(rsp.text)
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
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
            self.logger.info(".... End test_125009_relatives_in_community ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-125-010")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": ""}),
                              (get_timestamp() + 300, {"code": 1, "msg": ""})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_125010_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-125-010).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125010_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
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
            self.logger.info(".... End test_125010_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-125-011")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 1, "msg": ""}),
                              (-1, {"status": 200, "code": 1, "msg": ""}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is not valid "}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is not valid "}),
                              (1.0, {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('a', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('中', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('*', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('1a', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('1中', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('1*', {"status": 400, "code": 0, "msg": "is not valid "}),
                              (' ', {"status": 400, "code": 0, "msg": "is not valid "}),
                              ('', {"status": 400, "code": 0, "msg": "is not valid "})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_125011_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-125-011).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_125011_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                allure.attach("Actual response content：", str(rsp.text))
                self.logger.info("Actual response content：{0}".format(rsp.text))
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
            self.logger.info(".... End test_125011_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-125-012")
    def test_125012_no_token(self):
        """ Test identity temp without token(FT-HTJK-125-012)."""
        self.logger.info(".... Start test_125012_no_token ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": None}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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
            self.logger.info(".... End test_125012_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-125-013")
    def test_125013_no_member_id(self):
        """ Test identity temp without member_id(FT-HTJK-125-013)."""
        self.logger.info(".... Start test_125013_no_member_id ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 201001
                assert '授权非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125013_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少feature_name参数")
    @allure.testcase("FT-HTJK-125-014")
    def test_125014_no_feature_name(self):
        """ Test identity temp without feature_name(FT-HTJK-125-014)."""
        self.logger.info(".... Start test_125014_no_feature_name ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 201903
                assert '采集失败' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125014_no_feature_name ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少temp_photo参数")
    @allure.testcase("FT-HTJK-125-015")
    def test_125015_no_temp_photo(self):
        """ Test identity temp without temp_photo(FT-HTJK-125-015)."""
        self.logger.info(".... Start test_125015_no_temp_photo ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 500

        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125015_no_temp_photo ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-125-016")
    def test_125016_no_timestamp(self):
        """ Test identity temp without timestamp(FT-HTJK-125-016)."""
        self.logger.info(".... Start test_125016_no_timestamp ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli'}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep5: assert the response content"):
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
            self.logger.info(".... End test_125016_no_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("feature_sex值")
    @allure.testcase("FT-HTJK-125-017")
    @pytest.mark.parametrize("feature_sex, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (2, {"status": 200, "code": 1, "msg": ""}),
                              ('1', {"status": 200, "code": 1, "msg": ""}),
                              ('1' * 50, {"status": 400, "code": 1, "msg": ""}),
                              ('a', {"status": 400, "code": 1, "msg": ""}),
                              ('中', {"status": 400, "code": 1, "msg": ""}),
                              ('(*.)', {"status": 400, "code": 1, "msg": ""}),
                              ('1a*中', {"status": 400, "code": 1, "msg": ""}),
                              (1.123, {"status": 400, "code": 1, "msg": ""}),
                              (' ', {"status": 400, "code": 1, "msg": ""}),
                              ('', {"status": 400, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 1, "msg": ""}),
                              (3, {"status": 200, "code": 1, "msg": ""}),
                              (4, {"status": 200, "code": 1, "msg": ""})],
                             ids=["feature_sex(1)", "feature_sex(2)", "feature_sex(最小长度值)", "feature_sex(最大长度值)",
                                  "feature_sex(字母)", "feature_sex(中文)", "feature_sex(特殊字符)",
                                  "feature_sex(数字字母中文特殊字符)", "feature_sex(小数)", "feature_sex(空格)",
                                  "feature_sex(空)", "feature_sex(0)", "feature_sex(3)", "feature_sex(4)"])
    def test_125017_identity_temp_feature_sex_correct(self, feature_sex, result):
        """ Test identity temp by correct feature_sex(FT-HTJK-125-017)."""
        self.logger.info(".... Start test_125017_identity_temp_feature_sex_correct ({}) ....".format(feature_sex))
        try:
            with allure.step("teststep1: identity user."):
                with allure.step("teststep: user feature."):
                    headers = {"authorization": self.token}
                    self.httpclient.update_header(headers)
                    identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                     get_timestamp(), self.logger)
                    allure.attach("upload user feature result", "{0}".format(identity_result))
                    self.logger.info("upload user feature result: {0}".format(identity_result))

                with allure.step("teststep: identity user."):
                    headers = {"authorization": self.token}
                    self.httpclient.update_header(headers)
                    identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                    get_timestamp(), self.logger)
                    allure.attach("identity owner result", "{0}".format(identity_result))
                    self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "feature_name": 'kuli', "feature_sex": feature_sex, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"temp_photo": open(get_image_path('relate_face.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))
                self.logger.info("request.url: {}".format(rsp.request.url))

            with allure.step("teststep4: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == result['status']
                if rsp.status_code == 200:
                    rsp_content = rsp.json()
                else:
                    rsp_content = rsp.text

            with allure.step("teststep5: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                if rsp.status_code == 200:
                    assert rsp_content["code"] == result['code']
                    assert not rsp_content['message']
                    assert rsp_content['result']['feature_id']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_125017_identity_temp_feature_sex_correct ({}) ....".format(feature_sex))
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_APP_Identity_Temp.py'])
    # pytest.main(['-s', 'test_APP_Identity_Temp.py::TestIdentityTemp::test_125017_identity_temp_feature_sex_correct'])
