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


@allure.feature("APP-修改头像")
class TestModifyHeadImage(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'ModifyHeadImage')
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
    @allure.story("正确修改头像")
    @allure.testcase("FT-HTJK-109-001")
    def test_109001_modify_head_image_correct(self):
        """ Test modify head image by correct parameters(FT-HTJK-109-001)."""
        self.logger.info(".... Start test_109001_modify_head_image_correct ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                # files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                files = [('head_image',('Kaola.jpg', open(get_image_path('Kaola.jpg'), 'rb'), 'image/jpg'))]
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
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
                assert '修改头像成功' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image'] == rsp_content['result']['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109001_modify_head_image_correct ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误token值")
    @allure.testcase("FT-HTJK-109-002")
    @pytest.mark.parametrize("token, result",
                             [('1' * 256, {"code": 201001, "msg": "授权非法"}), ('1.0', {"code": 201001, "msg": "授权非法"}),
                              ('*', {"code": 201001, "msg": "授权非法"}), ('1*', {"code": 201001, "msg": "授权非法"}),
                              ('', {"code": 201000, "msg": "未登录或登录已过期"})],
                             ids=["token(超长值)", "token(小数)", "token(特殊字符)",
                                  "token(数字特殊字符)", "token(空)"])
    def test_109002_token_wrong(self, token, result):
        """ Test modify head image by wrong token(FT-HTJK-109-002).
        :param token: token parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109002_token_wrong ({0}) ....".format(token))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                # allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                # self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109002_token_wrong ({0}) ....".format(token))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误member_id值")
    @allure.testcase("FT-HTJK-109-003")
    @pytest.mark.parametrize("member_id, result",
                             [('1' * 256, {"status": 400, "code": 0, "msg": ""}),
                              (1.0, {"status": 400, "code": 0, "msg": ""}),
                              ('中', {"status": 400, "code": 0, "msg": ""}),
                              ('*', {"status": 400, "code": 0, "msg": ""}),
                              ('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),
                              (' ', {"status": 400, "code": 0, "msg": ""}),
                              ('', {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 201203, "msg": "保存头像失败[拉取用户信息失败]"}),
                              (9223372036854775808, {"status": 400, "code": 0, "msg": ""})],
                             ids=["member_id(超长值)", "member_id(小数)", "member_id(中文)",
                                  "member_id(特殊字符)", "member_id(数字中文)",
                                  "member_id(数字特殊字符)", "member_id(空格)", "member_id(空)",
                                  "member_id(0)", "member_id(超大)"])
    def test_109003_member_id_wrong(self, member_id, result):
        """ Test wrong member_id values (超长值、1.0、中文、特殊字符、数字中文、数字特殊字符、空格、空）(FT-HTJK-109-003).
        :param member_id: member_id parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109003_member_id_wrong ({0}) ....".format(member_id))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                # allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                # self.logger.info("request.body: {}".format(rsp.request.body))

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
                self.httpclient.update_header({"authorization": None})
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109003_member_id_wrong ({0}) ....".format(member_id))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("支持的图片类型")
    @allure.testcase("FT-HTJK-109-004")
    @pytest.mark.parametrize("filename, result",
                             [("Cat32px.png", {"code": 1, "msg": "修改头像成功"}),
                              ("Kaola.jpg", {"code": 1, "msg": "修改头像成功"}),
                              ("a1.jpeg", {"code": 1, "msg": "修改头像成功"}),
                              ("g2.gif", {"code": 1, "msg": "修改头像成功"}),
                              ("d1.bmp", {"code": 1, "msg": "修改头像成功"}),],
                             ids=["image(png)", "image(jpg)","image(jpeg)", "image(gif)","image(bmp)"])
    def test_109004_image_type_correct(self, filename, result):
        """ Test correct image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-109-004).
        :param filename: filename parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109004_image_type_correct ({}) ....".format(filename))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path(filename), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("filename", str(filename))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("filename: {}".format(filename))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image'] == rsp_content['result']['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109004_image_type_correct ({}) ....".format(filename))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("不支持的图片类型")
    @allure.testcase("FT-HTJK-109-005")
    @pytest.mark.parametrize("filename, result",
                             [("case.xlsx", {"code": 101000, "msg": ""}),
                              ("temp.txt", {"code": 101000, "msg": ""}),
                              ("hb.mp4", {"code": 101000, "msg": ""}),
                              ("max.jpg", {"code": 101000, "msg": ""}), ],
                             ids=["image(xlsx)", "image(txt)", "image(mp4)", "image(max)"])
    def test_109005_image_type_wrong(self, filename, result):
        """ Test wrong image type values (png/jpg/jpeg/bmp/gif）(FT-HTJK-109-005).
        :param filename: filename parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109005_image_type_wrong ({}) ....".format(filename))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path(filename), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("filename", str(filename))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("filename: {}".format(filename))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109005_image_type_wrong ({}) ....".format(filename))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-109-006")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 1, "msg": "修改头像成功"}),
                              (get_timestamp() + 300, {"code": 1, "msg": "修改头像成功"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_109006_timestamp_correct(self, timestamp, result):
        """ Test correct timestamp values (最小值、最大值）(FT-HTJK-109-006).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109006_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": timestamp}
                files = {"head_image": open(get_image_path('b1.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                self.logger.info("request.headers: {}".format(rsp.request.headers))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 200
                rsp_content = rsp.json()

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp_content))
                self.logger.info("response content: {}".format(rsp_content))
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image'] == rsp_content['result']['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109006_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-109-007")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 1, "msg": ""}),
                              (9223372036854775807, {"status": 200, "code": 1, "msg": ""}),
                              (0, {"status": 200, "code": 1, "msg": ""}),
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
    def test_109007_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-109-007).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_109007_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": timestamp}
                files = {"head_image": open(get_image_path('b1.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
                allure.attach("request.headers", str(rsp.request.headers))
                self.logger.info("request.headers: {}".format(rsp.request.headers))

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
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109007_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少token参数")
    @allure.testcase("FT-HTJK-109-008")
    def test_109008_no_token(self):
        """ Test modify head image without token(FT-HTJK-109-008)."""
        self.logger.info(".... Start test_109008_no_token ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": None}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
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
                assert rsp_content["code"] == 201000
                assert '未登录或登录已过期' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109008_no_token ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少member_id参数")
    @allure.testcase("FT-HTJK-109-009")
    def test_109009_no_member_id(self):
        """ Test modify head image without member_id(FT-HTJK-109-009)."""
        self.logger.info(".... Start test_109009_no_member_id ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
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
                assert rsp_content["code"] == 201203
                assert '保存头像失败' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109009_no_member_id ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少head_image参数")
    @allure.testcase("FT-HTJK-109-010")
    def test_109010_no_head_image(self):
        """ Test modify head image without head_image(FT-HTJK-109-010)."""
        self.logger.info(".... Start test_109010_no_head_image ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id, "timestamp": get_timestamp()}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.body", str(rsp.request.body))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.body: {}".format(rsp.request.body))

            with allure.step("teststep3: assert the response code"):
                allure.attach("Actual response code：", str(rsp.status_code))
                self.logger.info("Actual response code：{0}".format(rsp.status_code))
                assert rsp.status_code == 500

            with allure.step("teststep4: assert the response content"):
                allure.attach("response content：", str(rsp.text))
                self.logger.info("response content: {}".format(rsp.text))

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109010_no_head_image ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-109-011")
    def test_109011_no_timestamp(self):
        """ Test modify head image without timestamp(FT-HTJK-109-011)."""
        self.logger.info(".... Start test_109011_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                json = {"member_id": self.member_id}
                files = {"head_image": open(get_image_path('Kaola.jpg'), 'rb')}
                headers = {"authorization": self.token}
                allure.attach("params value", "{0}, {1}".format(json, headers))
                self.logger.info("data: {0}, headers: {1}".format(json, headers))

            with allure.step("teststep2: requests http post."):
                self.httpclient.update_header(headers)
                rsp = self.httpclient.post(self.URI, data=json, files=files)
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
                assert '修改头像成功' in rsp_content["message"]

            with allure.step("teststep5: check user info"):
                self.httpclient.update_header({"authorization": self.token})
                info = userinfo(self.httpclient, self.member_id, get_timestamp(), self.logger)
                allure.attach("user info：", str(info))
                self.logger.info("user info: {}".format(info))
                assert info['head_image']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_109011_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_APP_Modify_HeadImage.py'])
    pytest.main(['-s', 'test_APP_Modify_HeadImage.py::TestModifyHeadImage::test_109011_no_timestamp'])
