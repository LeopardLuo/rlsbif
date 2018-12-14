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
@allure.feature("APP-关联人身份认证")
class TestIdentityRelatives(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'IdentityOther')
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
                        "imei": "460011234567890", "phone": "13511222171", "sms_code": "123456",
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
    @allure.story("认证成功")
    @allure.testcase("FT-HTJK-117-001")
    def test_117001_identity_relatives_correct(self):
        """ Test identity relatives by correct parameters(FT-HTJK-117-001)."""
        self.logger.info(".... Start test_117001_identity_relatives_correct ....")
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
                params = {"member_id": self.member_id, "features_name": 'kuli', "feature_sex": 1, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))
                self.logger.info("request file: {}".format(str(files)))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
                assert '添加成员成功' in rsp_content['message']
                assert not rsp_content['result']

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
            self.logger.info(".... End test_117001_identity_relatives_correct ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("用户未认证，认证关联人")
    @allure.testcase("FT-HTJK-117-002")
    def test_117002_identity_relatives_without_user(self):
        """ Test identity relatives without user identity(FT-HTJK-117-002)."""
        self.logger.info(".... Start test_117002_identity_relatives_without_user ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
                print(rsp.text)
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == 201307
                assert '请先完成本人照片采集' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117002_identity_relatives_without_user ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-117-003")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_117003_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-117-003).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117003_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117003_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-117-004")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 201307, "msg": "请先完成本人照片采集"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_117004_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-117-004).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117004_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117004_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确features_name值")
    @allure.testcase("FT-HTJK-117-005")
    @pytest.mark.parametrize("features_name, result",
                             [('1', {"code": 1, "msg": "添加成员成功"}), ('1' * 50, {"code": 1, "msg": "添加成员成功"}),
                              ('abcd', {"code": 1, "msg": "添加成员成功"}), ('中中中中', {"code": 1, "msg": "添加成员成功"}),
                              ('(*.)', {"code": 1, "msg": "添加成员成功"}), ('1a*中', {"code": 1, "msg": "添加成员成功"}),
                              (1.123, {"code": 1, "msg": "添加成员成功"})],
                             ids=["features_name(最小长度值)", "features_name(最大长度值)", "features_name(字母)",
                                  "features_name(中文)", "features_name(特殊字符)", "features_name(数字字母中文特殊字符)", "features_name(小数)", ])
    def test_117005_features_name_correct(self, features_name, result):
        """ Test correct features_name values (最小长度值、最大长度值、字母、中文、特殊字符、数字字母中文特殊字符、空格、空）(FT-HTJK-117-005).
        :param features_name: features_name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117005_features_name_correct ({}) ....".format(features_name))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": features_name, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117005_features_name_correct ({}) ....".format(features_name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误features_name值")
    @allure.testcase("FT-HTJK-117-006")
    @pytest.mark.parametrize("features_name, result",
                             [('1' * 101, {"code": 201903, "msg": "添加成员失败"}),
                              ('     ', {"code": 201903, "msg": "添加成员失败"}), ('', {"code": 201903, "msg": "添加成员失败"})],
                             ids=["features_name(超长值)", "features_name(空格)", "features_name(空)"])
    def test_117006_features_name_wrong(self, features_name, result):
        """ Test wrong features_name values (超长值、空格、空）(FT-HTJK-117-006).
        :param features_name: features_name parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117006_features_name_wrong ({}) ....".format(features_name))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": features_name, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117006_features_name_wrong ({}) ....".format(features_name))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("other_photo支持的图片类型")
    @allure.testcase("FT-HTJK-117-007")
    @pytest.mark.parametrize("other_photo, result",
                             [("relate_face.png", {"code": 1, "msg": "添加成员成功"}),
                              ("relate_face.jpg", {"code": 1, "msg": "添加成员成功"}),
                              ("relate_face.jpeg", {"code": 1, "msg": "添加成员成功"}),
                              ("relate_face.tif", {"code": 1, "msg": "添加成员成功"}),
                              ("relate_face.bmp", {"code": 1, "msg": "添加成员成功"}), ],
                             ids=["other_photo(png)", "other_photo(jpg)", "other_photo(jpeg)",
                                  "other_photo(tif)", "other_photo(bmp)"])
    def test_117007_other_photo_type_correct(self, other_photo, result):
        """ Test correct other_photo image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-117-007).
        :param other_photo: other_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117007_other_photo_type_correct ({}) ....".format(other_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path(other_photo), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117007_other_photo_type_correct ({}) ....".format(other_photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("other_photo不支持的文件类型")
    @allure.testcase("FT-HTJK-117-008")
    @pytest.mark.parametrize("other_photo, result",
                             [("relate_face.gif", {"code": 201412, "msg": "照片不合格"}),
                              ("case.xlsx", {"code": 201412, "msg": "照片不合格"}),
                              ("temp.txt", {"code": 201412, "msg": "照片不合格"}),
                              ("hb.mp4", {"code": 201412, "msg": "照片不合格"}),
                              ("dog5.jpg", {"code": 201412, "msg": "照片不合格"}), ],
                             ids=["other_photo(gif)", "other_photo(xlsx)", "other_photo(txt)",
                                  "other_photo(mp4)", "other_photo(other)"])
    def test_117008_other_photo_type_wrong(self, other_photo, result):
        """ Test wrong other_photo image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-117-008).
        :param other_photo: other_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117008_other_photo_type_wrong ({}) ....".format(other_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path(other_photo), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117008_other_photo_type_wrong ({}) ....".format(other_photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("my_photo支持的图片类型")
    @allure.testcase("FT-HTJK-117-009")
    @pytest.mark.parametrize("my_photo, result",
                             [("face2.png", {"code": 1, "msg": "添加成员成功"}),
                              ("face2.jpg", {"code": 1, "msg": "添加成员成功"}),
                              ("face2.jpeg", {"code": 1, "msg": "添加成员成功"}),
                              ("face2.tif", {"code": 1, "msg": "添加成员成功"}),
                              ("face2.bmp", {"code": 1, "msg": "添加成员成功"}), ],
                             ids=["my_photo(png)", "my_photo(jpg)", "my_photo(jpeg)",
                                  "my_photo(tif)", "my_photo(bmp)"])
    def test_117009_my_photo_type_correct(self, my_photo, result):
        """ Test correct my_photo image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-117-009).
        :param my_photo: my_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117009_my_photo_type_correct ({}) ....".format(my_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path(my_photo), 'rb')}
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
            self.logger.info(".... End test_117009_my_photo_type_correct ({}) ....".format(my_photo))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("my_photo不支持的文件类型")
    @allure.testcase("FT-HTJK-117-010")
    @pytest.mark.parametrize("my_photo, result",
                             [("face2.gif", {"code": 201307, "msg": "照片不合格"}),
                              ("case.xlsx", {"code": 201307, "msg": "照片不合格"}),
                              ("temp.txt", {"code": 201307, "msg": "照片不合格"}),
                              ("hb.mp4", {"code": 201307, "msg": "照片不合格"}),
                              ("face1.PNG", {"code": 201307, "msg": "验证不通过"}), ],
                             ids=["my_photo(gif)", "my_photo(xlsx)", "my_photo(txt)",
                                  "my_photo(mp4)", "my_photo(other)"])
    def test_117010_my_photo_type_wrong(self, my_photo, result):
        """ Test wrong my_photo image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-117-010).
        :param my_photo: my_photo parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117010_my_photo_type_wrong ({}) ....".format(my_photo))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path(my_photo), 'rb')}
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
            self.logger.info(".... End test_117010_my_photo_type_wrong ({}) ....".format(my_photo))
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("关联人在合拍照")
    @allure.testcase("FT-HTJK-117-011")
    def test_117011_relatives_in_community(self):
        """ Test relatives in communtity_picture(FT-HTJK-117-011)."""
        self.logger.info(".... Start test_117011_relatives_in_community ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('two.jpeg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
                assert '添加成员成功' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117011_relatives_in_community ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("会员在合拍照")
    @allure.testcase("FT-HTJK-117-012")
    def test_117012_user_in_community(self):
        """ Test user in communtity_picture(FT-HTJK-117-012)."""
        self.logger.info(".... Start test_117012_user_in_community ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('relate_com.jpg'), 'rb')}
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
                assert rsp_content["code"] == 201307
                assert '验证不通过' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117012_user_in_community ....")
            self.logger.info("")

    @allure.severity("blocker")
    @allure.story("会员和关联人在合拍照")
    @allure.testcase("FT-HTJK-117-013")
    def test_117013_all_in_community(self):
        """ Test all in communtity_picture(FT-HTJK-117-013)."""
        self.logger.info(".... Start test_117013_all_in_community ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_com.jpg'), 'rb'),
                         "my_photo": open(get_image_path('relate_com.jpg'), 'rb')}
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
                assert rsp_content["code"] == 201307
                assert '验证不通过' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117013_all_in_community ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-117-014")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": "添加成员成功"}),
                              (get_timestamp() + 300, {"code": 1, "msg": "添加成员成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_117014_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-117-014).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117014_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117014_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-117-015")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              (0, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              (-1, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              (-9223372036854775809, {"status": 400, "code": 0, "msg": "is not valid"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": "is not valid"}),
                              (1.0, {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('a', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('中', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('*', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1a', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1中', {"status": 400, "code": 0, "msg": "is not valid"}),
                              ('1*', {"status": 400, "code": 0, "msg": "is not valid"}),
                              (' ', {"status": 400, "code": 0, "msg": "is invalid"}),
                              ('', {"status": 400, "code": 0, "msg": "is invalid"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)", "timestamp(0)", "timestamp(-1)",
                                  "timestamp(超小值)", "timestamp(超大值)", "timestamp(小数)",
                                  "timestamp(字母)", "timestamp(中文)", "timestamp(特殊字符)", "timestamp(数字字母)",
                                  "timestamp(数字中文)",
                                  "timestamp(数字特殊字符)", "timestamp(空格)", "timestamp(空)"])
    def test_117015_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-117-015).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_117015_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117015_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-117-016")
    def test_117016_no_token(self):
        """ Test identity relatives without token(FT-HTJK-117-016)."""
        self.logger.info(".... Start test_117016_no_token ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": None}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117016_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-117-017")
    def test_117017_no_member_id(self):
        """ Test identity relatives without member_id(FT-HTJK-117-017)."""
        self.logger.info(".... Start test_117017_no_member_id ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 201307
                assert '请先完成本人照片采集' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117017_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少features_name参数")
    @allure.testcase("FT-HTJK-117-018")
    def test_117018_no_features_name(self):
        """ Test identity relatives without features_name(FT-HTJK-117-018)."""
        self.logger.info(".... Start test_117018_no_features_name ....")
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
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
                assert '添加成员失败' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117018_no_features_name ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少other_photo参数")
    @allure.testcase("FT-HTJK-117-019")
    def test_117019_no_other_photo(self):
        """ Test identity relatives without other_photo(FT-HTJK-117-019)."""
        self.logger.info(".... Start test_117019_no_other_photo ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
            self.logger.info(".... End test_117019_no_other_photo ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少my_photo参数")
    @allure.testcase("FT-HTJK-117-020")
    def test_117020_no_my_photo(self):
        """ Test identity relatives without my_photo(FT-HTJK-117-020)."""
        self.logger.info(".... Start test_117020_no_my_photo ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli', "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb')}
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
            self.logger.info(".... End test_117020_no_my_photo ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-117-021")
    def test_117021_no_timestamp(self):
        """ Test identity relatives without timestamp(FT-HTJK-117-021)."""
        self.logger.info(".... Start test_117021_no_timestamp ....")
        try:
            with allure.step("teststep1: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep2: get parameters."):
                params = {"member_id": self.member_id, "features_name": 'kuli'}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
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
                assert '添加成员成功' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117021_no_timestamp ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确feature_sex值")
    @allure.testcase("FT-HTJK-117-022")
    @pytest.mark.parametrize("feature_sex, result",
                             [(1, {"status": 200, "code": 1, "msg": "添加成员成功"}), (2, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              ('1', {"status": 200, "code": 1, "msg": "添加成员成功"}), ('1' * 50, {"status": 400, "code": 1, "msg": "添加成员成功"}),
                              ('a', {"status": 400, "code": 1, "msg": "添加成员成功"}), ('中', {"status": 400, "code": 1, "msg": "添加成员成功"}),
                              ('(*.)', {"status": 400, "code": 1, "msg": "添加成员成功"}), ('1a*中', {"status": 400, "code": 1, "msg": "添加成员成功"}),
                              (1.123, {"status": 400, "code": 1, "msg": "添加成员成功"}), (' ', {"status": 400, "code": 1, "msg": "添加成员成功"}),
                              ('', {"status": 400, "code": 1, "msg": "添加成员成功"}), (0, {"status": 200, "code": 1, "msg": "添加成员成功"}),
                              (3, {"status": 200, "code": 1, "msg": "添加成员成功"}),(4, {"status": 200, "code": 1, "msg": "添加成员成功"})],
                             ids=["feature_sex(1)", "feature_sex(2)", "feature_sex(最小长度值)", "feature_sex(最大长度值)",
                                  "feature_sex(字母)",  "feature_sex(中文)", "feature_sex(特殊字符)",
                                  "feature_sex(数字字母中文特殊字符)", "feature_sex(小数)", "feature_sex(空格)",
                                  "feature_sex(空)", "feature_sex(0)", "feature_sex(3)", "feature_sex(4)"])
    def test_117022_identity_relatives_feature_sex_correct(self, feature_sex, result):
        """ Test identity relatives by correct feature_sex(FT-HTJK-117-022)."""
        self.logger.info(".... Start test_117022_identity_relatives_feature_sex_correct ({}) ....".format(feature_sex))
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
                params = {"member_id": self.member_id, "features_name": 'kuli', "feature_sex": feature_sex, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"other_photo": open(get_image_path('relate_face.jpg'), 'rb'),
                         "my_photo": open(get_image_path('face2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))
                self.logger.info("request file: {}".format(str(files)))

            with allure.step("teststep3: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
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
                    assert result['msg'] in rsp_content['message']
                    assert not rsp_content['result']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_117022_identity_relatives_feature_sex_correct ({}) ....".format(feature_sex))
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Identity_Relatives.py'])
    pytest.main(['-s', 'test_APP_Identity_Relatives.py::TestIdentityRelatives::test_117022_identity_relatives_feature_sex_correct'])
