#!/usr/bin/env python3
# -*-coding:utf-8-*-

import datetime
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
@allure.feature("H5-拜访申请服务单")
class TestShoppingBecomeVisitorResult(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'H5ShoppingBecomeVisitorResult')
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
    @allure.story("在白名单下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_with_whitelist(self):
        """ Test become visitor result interface with whitelist"""
        self.logger.info(".... Start test_become_visitor_result_with_whitelist ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-4", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == owner_feautreid
                assert select_result[0][7] == '本人'
                assert select_result[0][8] == 0
                assert select_result[0][9] == 0
                assert begin_time == "2014-12-04"
                assert end_time == "2028-12-11"

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][5] == '13511229000'
                assert select_result[0][6] == owner_feautreid
                assert select_result[0][7] == '本人'
                assert select_result[0][9] == 0
                assert select_result[0][12] == 1
                assert begin_time2 == begin_time
                assert end_time2 == end_time

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_with_whitelist ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("不在白名单下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_whitelist(self):
        """ Test become visitor result interface without whitelist"""
        self.logger.info(".... Start test_become_visitor_result_without_whitelist ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
                        "imei": "460011234567890", "phone": "13511229100", "sms_code": "123456",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][5] == '13511229100'
                assert select_result[0][6] == owner_feautreid
                assert select_result[0][7] == '本人'
                assert select_result[0][9] == 0
                assert select_result[0][12] == 0
                assert begin_time2 == "2014-12-04"
                assert end_time2 == "2028-12-11"

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_whitelist ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("没有登录下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_login(self):
        """ Test become visitor result interface without login."""
        self.logger.info(".... Start test_become_visitor_result_without_login ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
                with allure.step("初始化HTTP客户端。"):
                    h5_port = self.config.getItem('h5', 'port')
                    baseurl = '{0}://{1}:{2}'.format(self.sv_protocol, self.sv_host, h5_port)
                    allure.attach("baseurl", str(baseurl))
                    self.logger.info("baseurl: " + baseurl)
                    httpclient1 = HTTPClient(baseurl)
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用时间或次数单品下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_with_time_or_count(self):
        """ Test become visitor result interface with time or count"""
        self.logger.info(".... Start test_become_visitor_result_with_time_or_count ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert begin_time == "2014-12-04"
                assert end_time == "2028-12-11"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][11] == sku_price
                assert select_result[0][12] == 1
                assert begin_time2 == begin_time
                assert end_time2 == end_time
                assert select_result[0][17] == 0
                assert select_result[0][19] == 1

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_with_time_or_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用时间单品下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_with_time(self):
        """ Test become visitor result interface with time."""
        self.logger.info(".... Start test_become_visitor_result_with_time ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert begin_time == "2014-12-04"
                assert end_time == "2028-12-11"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][11] == sku_price
                assert select_result[0][12] == 1
                assert begin_time2 == begin_time
                assert end_time2 == end_time
                assert select_result[0][17] == 0
                assert select_result[0][19] == 1

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_with_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用次数单品下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_with_count(self):
        """ Test become visitor result interface with count."""
        self.logger.info(".... Start test_become_visitor_result_with_count ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert begin_time == "2014-12-04"
                assert end_time == "2028-12-11"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][11] == sku_price
                assert select_result[0][12] == 1
                assert begin_time2 == begin_time
                assert end_time2 == end_time
                assert select_result[0][17] == 0
                assert select_result[0][19] == 1

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_with_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用无限单品下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_with_forever(self):
        """ Test become visitor result interface with forever."""
        self.logger.info(".... Start test_become_visitor_result_with_forever ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert begin_time == "2014-12-04"
                assert end_time == "2028-12-11"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

            with allure.step("teststep10: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1
                begin_time2 = str(select_result[0][15].strftime("%Y-%m-%d"))
                end_time2 = str(select_result[0][16].strftime("%Y-%m-%d"))
                self.logger.info("begin_time: {0}".format(begin_time2))
                self.logger.info("end_time: {0}".format(end_time2))
                assert select_result[0][11] == sku_price
                assert select_result[0][12] == 1
                assert begin_time2 == begin_time
                assert end_time2 == end_time
                assert select_result[0][17] == 0
                assert select_result[0][19] == 1

            with allure.step("teststep11: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_with_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("没有认证下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_identity(self):
        """ Test become visitor result interface without identity."""
        self.logger.info(".... Start test_become_visitor_result_without_identity ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep4: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep5: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep6: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep7: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep8: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_identity ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("没有上传特征下拜访服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_user_feature(self):
        """ Test become visitor result interface without user feature."""
        self.logger.info(".... Start test_become_visitor_result_without_user_feature ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep3: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep4: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep5: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_time_or_count')
                sku_id = 0
                sku_price = -1
                sku_check_type = -1
                sku_begin_time = ''
                sku_end_time = ''
                sku_in_count = -1
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]
                        sku_price = item[3]
                        sku_check_type = item[12]
                        sku_begin_time = str(item[14].strftime("%Y-%m-%d"))
                        sku_end_time = str(item[15].strftime("%Y-%m-%d"))
                        sku_in_count = item[16]

            with allure.step("teststep6: create service orders"):
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
                with allure.step("拜访申请下单"):
                    r_applyresult1 = h5_shopping_become_visitor_result(httpclient1, provider_id, spu_id, sku_id, "2014-12-04", "2028-12-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep7: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}'".format(self.member_id))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep8: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_user_feature ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误providerId值")
    @allure.testcase("FT-HTJK-xxx-xxx")
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
                              (11111, {"status": 200, "code": '301', "msg": "该服务商已停止服务"}),
                              (0, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (-1, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["providerId(超长值)", "providerId(小数)", "providerId(英文)", "providerId(中文)",
                                  "providerId(特殊字符)", "providerId(数字英文)", "providerId(数字中文)",
                                  "providerId(数字特殊字符)", "providerId(空格)", "providerId(空)",
                                  "providerId(1)", "providerId(0)", "providerId(-1)", "providerId(超大)",
                                  "providerId(超小)"])
    def test_become_visitor_result_providerid_wrong(self, providerId, result):
        """ Test wrong providerId values (FT-HTJK-xxx-xxx).
        :param providerId: providerId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_become_visitor_result_providerid_wrong ({}) ....".format(providerId))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": providerId, "productId": spu_id, "skuId": sku_id,
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == result['status']
                        if rsp.status_code == 200:
                            rsp_content = rsp.json()
                        else:
                            rsp_content = rsp.text
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        if rsp.status_code == 200:
                            if 'code' in rsp_content.keys():
                                assert rsp_content["code"] == result['code']
                            else:
                                assert rsp_content["status"] == result['code']
                            assert result['msg'] in rsp_content["message"]
                        else:
                            assert result['msg'] in rsp.text

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_providerid_wrong ({}) ....".format(providerId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误productId值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("productId, result",
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
                              (11111, {"status": 200, "code": '301', "msg": "该产品未上架"}),
                              (0, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (-1, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["productId(超长值)", "productId(小数)", "productId(英文)", "productId(中文)",
                                  "productId(特殊字符)", "productId(数字英文)", "productId(数字中文)",
                                  "productId(数字特殊字符)", "productId(空格)", "productId(空)",
                                  "productId(1)", "productId(0)", "productId(-1)", "productId(超大)",
                                  "productId(超小)"])
    def test_become_visitor_result_productid_wrong(self, productId, result):
        """ Test wrong productId values (FT-HTJK-xxx-xxx).
        :param productId: productId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_become_visitor_result_productid_wrong ({}) ....".format(productId))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": productId, "skuId": sku_id,
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == result['status']
                        if rsp.status_code == 200:
                            rsp_content = rsp.json()
                        else:
                            rsp_content = rsp.text
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        if rsp.status_code == 200:
                            if 'code' in rsp_content.keys():
                                assert rsp_content["code"] == result['code']
                            else:
                                assert rsp_content["status"] == result['code']
                            assert result['msg'] in rsp_content["message"]
                        else:
                            assert result['msg'] in rsp.text

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_productid_wrong ({}) ....".format(productId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误skuId值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("skuId, result",
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
                              (11111, {"status": 200, "code": '301', "msg": "该服务未上架"}),
                              (0, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (-1, {"status": 200, "code": '300', "msg": "提交信息无效"}),
                              (9223372036854775808, {"status": 200, "code": 97, "msg": "参数格式不正确"}),
                              (-9223372036854775809, {"status": 200, "code": 97, "msg": "参数格式不正确"})],
                             ids=["skuId(超长值)", "skuId(小数)", "skuId(英文)", "skuId(中文)",
                                  "skuId(特殊字符)", "skuId(数字英文)", "skuId(数字中文)",
                                  "skuId(数字特殊字符)", "skuId(空格)", "skuId(空)",
                                  "skuId(1)", "skuId(0)", "skuId(-1)", "skuId(超大)", "skuId(超小)"])
    def test_become_visitor_result_skuid_wrong(self, skuId, result):
        """ Test wrong skuId values (FT-HTJK-xxx-xxx).
        :param skuId: skuId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_become_visitor_result_skuid_wrong ({}) ....".format(skuId))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": skuId,
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == result['status']
                        if rsp.status_code == 200:
                            rsp_content = rsp.json()
                        else:
                            rsp_content = rsp.text
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        if rsp.status_code == 200:
                            if 'code' in rsp_content.keys():
                                assert rsp_content["code"] == result['code']
                            else:
                                assert rsp_content["status"] == result['code']
                            assert result['msg'] in rsp_content["message"]
                        else:
                            assert result['msg'] in rsp.text

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_skuid_wrong ({}) ....".format(skuId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误beginTime值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("beginTime, result",
                             [(1.5, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (1, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (2000000000, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ("0001-01-01 01:01:01", {"status": 200, "code": '300', "msg": "提交邀请失败"}),
                              ('a', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('中', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('*', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('1a', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('1中', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('%1%', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (' ', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('2030-01-01', {"status": 200, "code": '300', "msg": "提交邀请失败(平台:结束时间必须晚于开始时间)"}),
                              ('2025-01-01', {"status": 200, "code": '300', "msg": "提交邀请失败(平台:结束时间必须晚于开始时间)"}),
                              (-1, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (9223372036854775808, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (-9223372036854775809, {"status": 200, "code": '300', "msg": "输入时间格式有误"})],
                             ids=["beginTime(1.5)", "beginTime(1)", "beginTime(20000000000)", "beginTime(格式化)",
                                  "beginTime(英文)", "beginTime(中文)",
                                  "beginTime(特殊字符)", "beginTime(数字英文)", "beginTime(数字中文)",
                                  "beginTime(数字特殊字符)", "beginTime(空格)", "beginTime(空)",
                                  "beginTime(1)", "beginTime(0)", "beginTime(-1)", "beginTime(超大)", "beginTime(超小)"])
    def test_become_visitor_result_begintime_wrong(self, beginTime, result):
        """ Test wrong beginTime values (FT-HTJK-xxx-xxx).
        :param beginTime: beginTime parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_become_visitor_result_begintime_wrong ({}) ....".format(beginTime))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "beginTime": beginTime, "endTime": '2030-01-01'}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == result['status']
                        if rsp.status_code == 200:
                            rsp_content = rsp.json()
                        else:
                            rsp_content = rsp.text
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        if rsp.status_code == 200:
                            if 'code' in rsp_content.keys():
                                assert rsp_content["code"] == result['code']
                            else:
                                assert rsp_content["status"] == result['code']
                            assert result['msg'] in rsp_content["message"]
                        else:
                            assert result['msg'] in rsp.text

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_begintime_wrong ({}) ....".format(beginTime))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("错误endTime值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("endTime, result",
                             [(1.5, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (1, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (2000000000, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ("0001-01-01 01:01:01", {"status": 200, "code": '300', "msg": "提交邀请失败"}),
                              ('a', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('中', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('*', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('1a', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('1中', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('%1%', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (' ', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('', {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              ('2030-01-01', {"status": 200, "code": '300', "msg": "提交邀请失败(平台:结束时间必须晚于开始时间)"}),
                              ('2025-01-01', {"status": 200, "code": '300', "msg": "提交邀请失败(平台:结束时间必须晚于开始时间)"}),
                              (-1, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (9223372036854775808, {"status": 200, "code": '300', "msg": "输入时间格式有误"}),
                              (-9223372036854775809, {"status": 200, "code": '300', "msg": "输入时间格式有误"})],
                             ids=["endTime(1.5)", "endTime(1)", "endTime(20000000000)", "endTime(格式化)",
                                  "endTime(英文)", "endTime(中文)",
                                  "endTime(特殊字符)", "endTime(数字英文)", "endTime(数字中文)",
                                  "endTime(数字特殊字符)", "endTime(空格)", "endTime(空)",
                                  "endTime(1)", "endTime(0)", "endTime(-1)", "endTime(超大)", "endTime(超小)"])
    def test_become_visitor_result_endtime_wrong(self, endTime, result):
        """ Test wrong endTime values (FT-HTJK-xxx-xxx).
        :param endTime: endTime parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_become_visitor_result_endtime_wrong ({}) ....".format(endTime))
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "beginTime": "2025-01-01", "endTime": endTime}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == result['status']
                        if rsp.status_code == 200:
                            rsp_content = rsp.json()
                        else:
                            rsp_content = rsp.text
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        if rsp.status_code == 200:
                            if 'code' in rsp_content.keys():
                                assert rsp_content["code"] == result['code']
                            else:
                                assert rsp_content["status"] == result['code']
                            assert result['msg'] in rsp_content["message"]
                        else:
                            assert result['msg'] in rsp.text

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_endtime_wrong ({}) ....".format(endTime))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少providerId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_providerid(self):
        """ Test become visitor result without providerId (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_become_visitor_result_without_providerid ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"productId": spu_id, "skuId": sku_id,
                                "beginTime": "2020-01-01", "endTime": "2022-01-01"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert '' in rsp_content["message"]

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_providerid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少productId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_productid(self):
        """ Test become visitor result without productId (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_become_visitor_result_without_productid ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "skuId": sku_id,
                                "beginTime": "2020-01-01", "endTime": "2022-01-01"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert '' in rsp_content["message"]

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_productid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少skuId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_skuid(self):
        """ Test become visitor result without skuId (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_become_visitor_result_without_skuid ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id,
                                "beginTime": "2020-01-01", "endTime": "2022-01-01"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert '' in rsp_content["message"]

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_skuid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少beginTime参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_begintime(self):
        """ Test become visitor result without beginTime (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_become_visitor_result_without_begintime ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id,
                                "skuId": sku_id, "endTime": "2022-01-01"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert '' in rsp_content["message"]

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_begintime ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少endTime参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_become_visitor_result_without_endtime(self):
        """ Test become visitor result without endTime (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_become_visitor_result_without_endtime ....")
        try:
            with allure.step("teststep1: user register."):
                json = {"code_type": 0, "client_type": 1, "client_version": "v1", "device_token": "123456789",
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

            with allure.step("teststep2: user feature."):
                headers = {"authorization": self.token}
                self.httpclient.update_header(headers)
                identity_result = user_myfeature(self.httpclient, self.member_id, 'face2.jpg',
                                                 get_timestamp(), self.logger)
                allure.attach("upload user feature result", "{0}".format(identity_result))
                self.logger.info("upload user feature result: {0}".format(identity_result))

            with allure.step("teststep3: identity user."):
                identity_result = user_identity(self.httpclient, self.member_id, 'fore2.jpg', 'back2.jpg',
                                                get_timestamp(), self.logger)
                allure.attach("identity owner result", "{0}".format(identity_result))
                self.logger.info("identity owner result: {0}".format(identity_result))

            with allure.step("teststep4: get provider id"):
                provider_name = self.config.getItem('h5', 'name')
                table = 'bus_provider'
                condition = ("name", provider_name)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                provider_id = select_result[0][0]

            with allure.step("teststep5: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep6: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_name = self.config.getItem('sku', 'single_forever')
                sku_id = 0
                for item in select_result:
                    if item[2] == sku_name:
                        sku_id = item[0]

            with allure.step("teststep7: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_featureid = select_result[0][0]

            with allure.step("teststep8: create service orders"):
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
                with allure.step("本人申请下单"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id,
                                "skuId": sku_id, "beginTime": "2020-01-01"}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert '' in rsp_content["message"]

            with allure.step("teststep9: user logout."):
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
            with allure.step("teststep: delete user features"):
                table = 'mem_features'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(select_result))
                self.logger.info("delete result: {0}".format(select_result))
            with allure.step("teststep: delete service order records"):
                table = 'bus_service_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete bus service order records"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            with allure.step("teststep: delete insert user info"):
                table = 'mem_member'
                condition = ("phone", "1351122%")
                allure.attach("table name", str(table))
                self.logger.info("table: {0}".format(table))
                delete_result = self.mysql.execute_delete_condition(table, condition)
                allure.attach("delete result", str(delete_result))
                self.logger.info("delete result: {0}".format(delete_result))
            self.logger.info(".... End test_become_visitor_result_without_endtime ....")
            self.logger.info("")


if __name__ == "__main__":
    pytest.main(['-s', 'test_H5_Shopping_BecomeVisitorResult.py::TestShoppingBecomeVisitorResult::test_become_visitor_result_without_user_feature'])
