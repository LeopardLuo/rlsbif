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
@allure.feature("APP-用户身份认证")
class TestIdentityUser(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'UserIdentity')
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
                        "imei": "460011234567890", "phone": "13511222161", "sms_code": "123456",
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
        with allure.step("delete mem_member_identity"):
            table = 'mem_member_identity'
            condition = ("member_id", self.member_id)
            allure.attach("table name and condition", "{0},{1}".format(table, condition))
            self.logger.info("delele records of table: {0}".format(table))
            delete_result = self.mysql.execute_delete_condition(table, condition)
            allure.attach("delete result", str(delete_result))
            self.logger.info("delete result: {0}".format(delete_result))
        self.logger.info("=== End teardown method ===")
        self.logger.info("")

    @allure.severity("blocker")
    @allure.story("身份认证成功")
    @allure.testcase("FT-HTJK-115-001")
    def test_115001_identity_user_correct(self):
        """ Test identity user by correct parameters(FT-HTJK-115-001)."""
        self.logger.info(".... Start test_115001_identity_user_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 1
                assert '认证通过' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115001_identity_user_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-115-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_115002_token_wrong(self, token, result):
        """ Test wrong token values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-115-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115002_token_wrong ({}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115002_token_wrong ({}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-115-003")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "member_id值非法"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_115003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-115-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115003_member_id_wrong ({}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115003_member_id_wrong ({}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("identity_card_face支持的图片类型")
    @allure.testcase("FT-HTJK-115-004")
    @pytest.mark.parametrize("identity_card_face, result",
                             [("fore2.png", {"code": 1, "msg": "认证通过"}),
                              ("fore2.jpg", {"code": 1, "msg": "认证通过"}),
                              ("fore2.jpeg", {"code": 1, "msg": "认证通过"}),
                              ("fore2.tif", {"code": 1, "msg": "认证通过"}),
                              ("fore2.bmp", {"code": 1, "msg": "认证通过"}), ],
                             ids=["identity_card_face(png)", "identity_card_face(jpg)", "identity_card_face(jpeg)",
                                  "identity_card_face(tif)", "identity_card_face(bmp)"])
    def test_115004_identity_card_face_type_correct(self, identity_card_face, result):
        """ Test correct identity_card_face image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-115-004).
        :param identity_card_face: identity_card_face parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115004_identity_card_face_type_correct ({}) ....".format(identity_card_face))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path(identity_card_face), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115004_identity_card_face_type_correct ({}) ....".format(identity_card_face))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("identity_card_face不支持的文件类型")
    @allure.testcase("FT-HTJK-115-005")
    @pytest.mark.parametrize("identity_card_face, result",
                             [("fore2.gif", {"code": 201307, "msg": "照片不合格"}),
                              ("case.xlsx", {"code": 201307, "msg": "照片不合格"}),
                              ("temp.txt", {"code": 201307, "msg": "照片不合格"}),
                              ("hb.mp4", {"code": 201307, "msg": "照片不合格"}),
                              ("fore1.PNG", {"code": 201307, "msg": "验证不通过"}), ],
                             ids=["identity_card_face(gif)", "identity_card_face(xlsx)", "identity_card_face(txt)",
                                  "identity_card_face(mp4)", "identity_card_face(other)"])
    def test_115005_identity_card_face_type_wrong(self, identity_card_face, result):
        """ Test wrong identity_card_face image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-115-005).
        :param identity_card_face: identity_card_face parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115005_identity_card_face_type_wrong ({}) ....".format(identity_card_face))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path(identity_card_face), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(
                ".... End test_115005_identity_card_face_type_wrong ({}) ....".format(identity_card_face))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("identity_card_emblem支持的图片类型")
    @allure.testcase("FT-HTJK-115-006")
    @pytest.mark.parametrize("identity_card_emblem, result",
                             [("back2.png", {"code": 1, "msg": "认证通过"}),
                              ("back2.jpg", {"code": 1, "msg": "认证通过"}),
                              ("back2.jpeg", {"code": 1, "msg": "认证通过"}),
                              ("back2.tif", {"code": 1, "msg": "认证通过"}),
                              ("back2.bmp", {"code": 1, "msg": "认证通过"}), ],
                             ids=["identity_card_emblem(png)", "identity_card_emblem(jpg)", "identity_card_emblem(jpeg)",
                                  "identity_card_emblem(tif)", "identity_card_emblem(bmp)"])
    def test_115006_identity_card_emblem_type_correct(self, identity_card_emblem, result):
        """ Test correct identity_card_emblem image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-115-006).
        :param identity_card_emblem: identity_card_emblem parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115006_identity_card_emblem_type_correct ({}) ....".format(identity_card_emblem))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path(identity_card_emblem), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(
                ".... End test_115006_identity_card_emblem_type_correct ({}) ....".format(identity_card_emblem))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("identity_card_emblem不支持的文件类型")
    @allure.testcase("FT-HTJK-115-007")
    @pytest.mark.parametrize("identity_card_emblem, result",
                             [("back2.gif", {"code": 201307, "msg": "照片不合格"}),
                              ("case.xlsx", {"code": 201307, "msg": "照片不合格"}),
                              ("temp.txt", {"code": 201307, "msg": "照片不合格"}),
                              ("hb.mp4", {"code": 201307, "msg": "照片不合格"}),
                              ("a1.jpeg", {"code": 201307, "msg": "照片不合格"}), ],
                             ids=["identity_card_emblem(gif)", "identity_card_emblem(xlsx)", "identity_card_emblem(txt)",
                                  "identity_card_emblem(mp4)", "identity_card_emblem(other)"])
    def test_115007_identity_card_emblem_type_wrong(self, identity_card_emblem, result):
        """ Test wrong identity_card_emblem image type values (gif/xlsx/txt/mp4/other）(FT-HTJK-115-007).
        :param identity_card_emblem: identity_card_emblem parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_115007_identity_card_emblem_type_wrong ({}) ....".format(identity_card_emblem))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path(identity_card_emblem), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(
                ".... End test_115007_identity_card_emblem_type_wrong ({}) ....".format(identity_card_emblem))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-115-010")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": "认证通过"}),
                              (get_timestamp() + 300, {"code": 1, "msg": "认证通过"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_115010_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-115-010).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(
            ".... Start test_115010_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(
                ".... End test_115010_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-115-011")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "timestamp不能为空"}),
                              (-1, {"status": 200, "code": 1, "msg": ""}),
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
    def test_115011_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-115-011).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(
            ".... Start test_115011_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": timestamp}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
                allure.attach("params value", "{0}, {1}".format(params, headers))
                self.logger.info("data: {0}, headers: {1}".format(params, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=params, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.files", str(files))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.files: {}".format(files))

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

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                if result['code'] != 1:
                    assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(
                ".... End test_115011_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-115-012")
    def test_115012_no_token(self):
        """ Test modify head image without token(FT-HTJK-115-012)."""
        self.logger.info(".... Start test_115012_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": None}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 201000
                assert '未登录或登录已过期' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115012_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-115-013")
    def test_115013_no_member_id(self):
        """ Test modify head image without member_id(FT-HTJK-115-013)."""
        self.logger.info(".... Start test_115013_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 101000
                assert 'member_id值非法' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115013_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少identity_card_face参数")
    @allure.testcase("FT-HTJK-115-014")
    def test_115014_no_identity_card_face(self):
        """ Test modify head image without identity_card_face(FT-HTJK-115-014)."""
        self.logger.info(".... Start test_115014_no_identity_card_face ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 101000
                assert 'identity_card_face值非法' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115014_no_identity_card_face ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少identity_card_emblem参数")
    @allure.testcase("FT-HTJK-115-015")
    def test_115015_no_identity_card_emblem(self):
        """ Test modify head image without identity_card_emblem(FT-HTJK-115-015)."""
        self.logger.info(".... Start test_115015_no_identity_card_emblem ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id, "timestamp": get_timestamp()}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 101000
                assert 'identity_card_emblem值非法' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115015_no_identity_card_emblem ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-115-017")
    def test_115017_no_timestamp(self):
        """ Test modify head image without timestamp(FT-HTJK-115-017)."""
        self.logger.info(".... Start test_115017_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"member_id": self.member_id}
                headers = {"authorization": self.token}
                files = {"identity_card_face": open(get_image_path('fore2.jpg'), 'rb'),
                         "identity_card_emblem": open(get_image_path('back2.jpg'), 'rb')}
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
                assert rsp_content["code"] == 101000
                assert 'timestamp不能为空' in rsp_content['message']

            with allure.step("teststep5: query database records"):
                table = 'mem_member_identity'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_115017_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Identity_User.py'])
    pytest.main(['-s', 'test_APP_Identity_User.py::TestIdentityUser::test_115017_no_timestamp'])
