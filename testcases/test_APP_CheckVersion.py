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


@pytest.mark.APP
@pytest.skip
@allure.feature("APP-获取版本信息")
class TestCheckVersion(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'CheckVersion')
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

            with allure.step("初始化MQTT客户端"):
                cls.devicename = cls.config.getItem('device', 'd1_devicename')
                cls.secret = cls.config.getItem('device', 'd1_secret')
                cls.productkey = cls.config.getItem('device', 'd1_productkey')
                cls.tp = cls.config.getItem('iot', 'ServiceOrderPush')
                allure.attach("device params", str((cls.devicename, cls.secret, cls.productkey)))
                cls.logger.info("device params: {}".format((cls.devicename, cls.secret, cls.productkey)))
                params = AliParam(ProductKey=cls.productkey, DeviceName=cls.devicename,
                                  DeviceSecret=cls.secret)
                clientid, username, password, hostname = params.get_param()
                cls.mqttclient = MqttClient(hostname, clientid, username, password)
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

    @allure.severity("critical")
    @allure.story("正确package_type值")
    @allure.testcase("FT-HTJK-126-001")
    @pytest.mark.parametrize("package_type, result",
                             [(1, {"code": 0, "msg": "当前版本已是最新版本"}), (2, {"code": 0, "msg": "当前版本已是最新版本"}),
                              (3, {"code": 0, "msg": "当前版本已是最新版本"})],
                             ids=["package_type(1)", "package_type(2)", "package_type(3)"])
    def test_126001_package_type_correct(self, package_type, result):
        """ Test check version with correct package_type(FT-HTJK-126-001)."""
        self.logger.info(".... Start test_126001_package_type_correct ({}) ....".format(package_type))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": package_type, "package_version": '1.0.0.0', "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content['message']
                if rsp_content["code"] == 1:
                    assert rsp_content['result']['data']['package_url']
                else:
                    assert not rsp_content['result']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126001_package_type_correct ({}) ....".format(package_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误package_type值")
    @allure.testcase("FT-HTJK-126-002")
    @pytest.mark.parametrize("package_type, result",
                             [(-2147483649, {"status": 400, "code": 0, "msg": ""}), (2147483648, {"status": 400, "code": 0, "msg": ""}),
                              (0, {"status": 200, "code": 101000, "msg": "package_type值非法"}),(4, {"status": 200, "code": 101000, "msg": "package_type值非法"}),(-1, {"status": 200, "code": 101000, "msg": "package_type值非法"}),
                              (1.5, {"status": 400, "code": 0, "msg": ""}),('a', {"status": 400, "code": 0, "msg": ""}),('中文', {"status": 400, "code": 0, "msg": ""}),
                              ('.*', {"status": 400, "code": 0, "msg": ""}),('1a', {"status": 400, "code": 0, "msg": ""}),('1中', {"status": 400, "code": 0, "msg": ""}),
                              ('1*', {"status": 400, "code": 0, "msg": ""}),(' ', {"status": 400, "code": 0, "msg": ""}),('', {"status": 400, "code": 0, "msg": ""}),],
                             ids=["package_type(-2147483649)", "package_type(2147483648)", "package_type(0)",
                                  "package_type(4)", "package_type(-1)", "package_type(1.5)","package_type(字母)",
                                  "package_type(中文)", "package_type(特殊字符)",  "package_type(数字字母)",
                                  "package_type(数字中文)",  "package_type(数字特殊字符)",  "package_type(空格)",
                                  "package_type(空)"])
    def test_126002_package_type_wrong(self, package_type, result):
        """ Test check version with wrong package_type(FT-HTJK-126-002)."""
        self.logger.info(".... Start test_126002_package_type_wrong ({}) ....".format(package_type))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": package_type, "package_version": '1.0.0.0', "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126002_package_type_wrong ({}) ....".format(package_type))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确package_version值")
    @allure.testcase("FT-HTJK-126-003")
    @pytest.mark.parametrize("package_version, result",
                             [('1.0.0.0', {"code": 0, "msg": "当前版本已是最新版本"}), ('99.99.99.99', {"code": 0, "msg": "当前版本已是最新版本"})],
                             ids=["package_version(最小值)", "package_version(最大值)"])
    def test_126003_package_version_correct(self, package_version, result):
        """ Test check version with correct package_version(FT-HTJK-126-003)."""
        self.logger.info(".... Start test_126003_package_version_correct ({}) ....".format(package_version))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "package_version": package_version, "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content['message']
                if rsp_content['code'] == 1:
                    assert rsp_content['result']['data']['package_url']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126003_package_version_correct ({}) ....".format(package_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误package_version值")
    @allure.testcase("FT-HTJK-126-004")
    @pytest.mark.parametrize("package_version, result",
                             [(0, {"code": 101000, "msg": "package_version值非法"}), (-1, {"code": 101000, "msg": "package_version值非法"}), (1.0, {"code": 101000, "msg": "package_version值非法"}),
                              ('1.0.0.9999', {"code": 101000, "msg": "package_version值非法"}), ('1.0.0.a', {"code": 101000, "msg": "package_version值非法"}),
                              ('1.0.0.中', {"code": 101000, "msg": "package_version值非法"}), ('1.0.0.*', {"code": 101000, "msg": "package_version值非法"}),
                              ('       ', {"code": 101000, "msg": "package_version值非法"}), ('', {"code": 101000, "msg": "package_version值非法"})],
                             ids=["package_version(0)", "package_version(-1)", "package_version(1.0)",
                                  "package_version(9999)", "package_version(字母)", "package_version(中文)",
                                  "package_version(特殊字符)", "package_version(空格)", "package_version(空)", ])
    def test_126004_package_version_wrong(self, package_version, result):
        """ Test check version with wrong package_version(FT-HTJK-126-003)."""
        self.logger.info(".... Start test_126004_package_version_wrong ({}) ....".format(package_version))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "package_version": package_version, "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == result['code']
                assert result['msg'] in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126004_package_version_wrong ({}) ....".format(package_version))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("正确timestamp值")
    @allure.testcase("FT-HTJK-126-005")
    @pytest.mark.parametrize("timestamp, result",
                             [(get_timestamp() - 300, {"code": 0, "msg": "当前版本已是最新版本"}),
                              (get_timestamp() + 300, {"code": 0, "msg": "当前版本已是最新版本"})],
                             ids=["timestamp(最小值)", "timestamp(最大值)"])
    def test_126005_timestamp_correct(self, timestamp, result):
        """ Test check version with correct timestamp(FT-HTJK-126-005)."""
        self.logger.info(".... Start test_126005_timestamp_correct ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "package_version": '1.0.0.0', "timestamp": timestamp}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert result['msg'] in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126005_timestamp_correct ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误timestamp值")
    @allure.testcase("FT-HTJK-126-006")
    @pytest.mark.parametrize("timestamp, result",
                             [(1, {"status": 200, "code": 0, "msg": "当前版本已是最新版本"}),
                              (9223372036854775807, {"status": 200, "code": 0, "msg": "当前版本已是最新版本"}),
                              (0, {"status": 200, "code": 0, "msg": "当前版本已是最新版本"}),
                              (-1, {"status": 200, "code": 0, "msg": "当前版本已是最新版本"}),
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
    def test_126006_timestamp_wrong(self, timestamp, result):
        """ Test wrong timestamp values (1、9223372036854775807、0、-1、-9223372036854775809、9223372036854775808、1.0、
            字母、中文、特殊字符、数字字母、数字中文、数字特殊字符、空格、空）(FT-HTJK-122-014).
        :param timestamp: timestamp parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_126006_timestamp_wrong ({}) ....".format(timestamp))
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "package_version": '1.0.0.0', "timestamp": timestamp}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
                allure.attach("request.headers", str(rsp.request.headers))
                allure.attach("request.url", str(rsp.request.url))
                self.logger.info("request.headers: {}".format(rsp.request.headers))
                self.logger.info("request.url: {}".format(rsp.request.url))

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
                    assert rsp_content["code"] == result['code']
                    assert result['msg'] in rsp_content['message']
                else:
                    assert result['msg'] in rsp_content
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126006_timestamp_wrong ({}) ....".format(timestamp))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少package_type参数")
    @allure.testcase("FT-HTJK-126-007")
    def test_126007_no_package_type(self):
        """ Test check version without package_type(FT-HTJK-126-007)."""
        self.logger.info(".... Start test_126007_no_package_type ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_version": '1.0.0.0', "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 101000
                assert 'package_type值非法' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126007_no_package_type ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少package_version参数")
    @allure.testcase("FT-HTJK-126-008")
    def test_126008_no_package_version(self):
        """ Test check version without package_version(FT-HTJK-126-008)."""
        self.logger.info(".... Start test_126008_no_package_version ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "timestamp": get_timestamp()}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 101000
                assert 'package_version' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126008_no_package_version ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少timestamp参数")
    @allure.testcase("FT-HTJK-126-009")
    def test_126009_no_timestamp(self):
        """ Test check version without timestamp(FT-HTJK-126-009)."""
        self.logger.info(".... Start test_126009_no_timestamp ....")
        try:
            with allure.step("teststep1: get parameters."):
                params = {"package_type": 2, "package_version": '1.0.0.0'}
                allure.attach("params value", "{0}".format(params))
                self.logger.info("data: {0}".format(params))

            with allure.step("teststep2: requests http get."):
                rsp = self.httpclient.get(self.URI, params=params)
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
                assert rsp_content["code"] == 101000
                assert 'timestamp值已过期' in rsp_content['message']
        except Exception as e:
            allure.attach("Exception: ", "{}".format(e))
            self.logger.error("Error: exception occur: ")
            self.logger.error(e)
            assert False
        finally:
            self.logger.info(".... End test_126009_no_timestamp ....")
            self.logger.info("")


if __name__ == '__main__':
    pytest.main(['-s', 'test_APP_CheckVersion.py::TestCheckVersion::test_126007_no_package_type'])
