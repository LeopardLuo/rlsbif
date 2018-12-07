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
@allure.feature("H5-邀请访客服务单")
class TestShoppingAddVisitorResult(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'H5ShoppingAddVisitorResult')
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
    @allure.story("在白名单下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_with_whitelist(self):
        """ Test add visitor result interface add other with whitelist"""
        self.logger.info(".... Start test_add_visitor_result_other_with_whitelist ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", time.strftime("%Y-%m-%d"), "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                features_id1 = select_result[0][0]
                relationship = select_result[0][3]
                assert relationship == 99

            with allure.step("teststep10: get bus_service_order info"):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                other_order = None
                for order in r_order:
                    if order['features_name'] == 'kuli1':
                        other_order = order
                assert other_order
                self.logger.info("other order : {0}".format(other_order))
                service_order_id = other_order['service_order_id']
                begin_time = str(datetime.datetime.fromtimestamp(other_order['begin_time'])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(other_order['end_time'])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert other_order['service_unit'] == provider_name
                assert other_order['features_id'] == features_id1
                assert other_order['relationships'] == 99
                assert other_order['features_type'] == 0
                assert begin_time == time.strftime("%Y-%m-%d")
                assert end_time == "2021-02-10"

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                for item in select_result:
                    if item[7] == 'kuli1':
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[4] == service_order_id
                        assert item[5] == ''
                        assert item[6] == features_id1
                        assert item[9] == 3
                        assert item[12] == 1
                        assert begin_time2 == time.strftime("%Y-%m-%d")
                        assert end_time2 == "2021-02-10"
                    else:
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[5] == '13511229000'
                        assert item[6] == owner_feautreid
                        assert item[7] == '本人'
                        assert item[9] == 0
                        assert item[12] == 1
                        assert begin_time2 == '2010-02-04'
                        assert end_time2 == '2038-02-11'

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_with_whitelist ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("不在白名单下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_without_whitelist(self):
        """ Test add visitor result interface add other without whitelist"""
        self.logger.info(".... Start test_add_visitor_result_other_without_whitelist ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", time.strftime("%Y-%m-%d"), "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep10: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_without_whitelist ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("给本人下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_user_with_whitelist(self):
        """ Test add visitor result interface add user with whitelist"""
        self.logger.info(".... Start test_add_visitor_result_user_with_whitelist ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "owner", time.strftime("%Y-%m-%d"), "2021-02-10", "face2.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep10: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_user_with_whitelist ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用时间或次数单品下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_with_time_or_count(self):
        """ Test add visitor result interface add other with time or count"""
        self.logger.info(".... Start test_add_visitor_result_other_with_time_or_count ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", "2014-06-21", "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                features_id1 = select_result[0][0]
                relationship = select_result[0][3]
                assert relationship == 99

            with allure.step("teststep10: get bus_service_order info"):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                other_order = None
                for order in r_order:
                    if order['features_name'] == 'kuli1':
                        other_order = order
                assert other_order
                self.logger.info("other order : {0}".format(other_order))
                service_order_id = other_order['service_order_id']
                begin_time = str(datetime.datetime.fromtimestamp(other_order['begin_time'])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(other_order['end_time'])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert other_order['service_unit'] == provider_name
                assert other_order['features_id'] == features_id1
                assert other_order['relationships'] == 99
                assert other_order['features_type'] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert other_order['in_count'] == 0
                assert other_order['verify_condition_type'] == 1

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                for item in select_result:
                    if item[7] == 'kuli1':
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[11] == sku_price
                        assert item[12] == 1
                        assert begin_time2 == begin_time
                        assert end_time2 == end_time
                        assert item[17] == 0
                        assert item[19] == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_with_time_or_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用时间单品下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_with_time(self):
        """ Test add visitor result interface add other with time"""
        self.logger.info(".... Start test_add_visitor_result_other_with_time ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", "2014-06-21", "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                features_id1 = select_result[0][0]
                relationship = select_result[0][3]
                assert relationship == 99

            with allure.step("teststep10: get bus_service_order info"):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                other_order = None
                for order in r_order:
                    if order['features_name'] == 'kuli1':
                        other_order = order
                assert other_order
                self.logger.info("other order : {0}".format(other_order))
                service_order_id = other_order['service_order_id']
                begin_time = str(datetime.datetime.fromtimestamp(other_order['begin_time'])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(other_order['end_time'])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert other_order['service_unit'] == provider_name
                assert other_order['features_id'] == features_id1
                assert other_order['relationships'] == 99
                assert other_order['features_type'] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert other_order['in_count'] == 0
                assert other_order['verify_condition_type'] == 1

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                for item in select_result:
                    if item[7] == 'kuli1':
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[11] == sku_price
                        assert item[12] == 1
                        assert begin_time2 == begin_time
                        assert end_time2 == end_time
                        assert item[17] == 0
                        assert item[19] == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_with_time ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用次数单品下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_with_count(self):
        """ Test add visitor result interface add other with count"""
        self.logger.info(".... Start test_add_visitor_result_other_with_count ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", "2014-06-21", "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                features_id1 = select_result[0][0]
                relationship = select_result[0][3]
                assert relationship == 99

            with allure.step("teststep10: get bus_service_order info"):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                other_order = None
                for order in r_order:
                    if order['features_name'] == 'kuli1':
                        other_order = order
                assert other_order
                self.logger.info("other order : {0}".format(other_order))
                service_order_id = other_order['service_order_id']
                begin_time = str(datetime.datetime.fromtimestamp(other_order['begin_time'])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(other_order['end_time'])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert other_order['service_unit'] == provider_name
                assert other_order['features_id'] == features_id1
                assert other_order['relationships'] == 99
                assert other_order['features_type'] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert other_order['in_count'] == 0
                assert other_order['verify_condition_type'] == 1

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                for item in select_result:
                    if item[7] == 'kuli1':
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[11] == sku_price
                        assert item[12] == 1
                        assert begin_time2 == begin_time
                        assert end_time2 == end_time
                        assert item[17] == 0
                        assert item[19] == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_with_count ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("使用无限单品下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_with_forever(self):
        """ Test add visitor result interface add other with forever"""
        self.logger.info(".... Start test_add_visitor_result_other_with_forever ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", "2014-06-21", "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                features_id1 = select_result[0][0]
                relationship = select_result[0][3]
                assert relationship == 99

            with allure.step("teststep10: get bus_service_order info"):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                other_order = None
                for order in r_order:
                    if order['features_name'] == 'kuli1':
                        other_order = order
                assert other_order
                self.logger.info("other order : {0}".format(other_order))
                service_order_id = other_order['service_order_id']
                begin_time = str(datetime.datetime.fromtimestamp(other_order['begin_time'])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(other_order['end_time'])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert other_order['service_unit'] == provider_name
                assert other_order['features_id'] == features_id1
                assert other_order['relationships'] == 99
                assert other_order['features_type'] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert other_order['in_count'] == 0
                assert other_order['verify_condition_type'] == 1

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                for item in select_result:
                    if item[7] == 'kuli1':
                        begin_time2 = str(item[15].strftime("%Y-%m-%d"))
                        end_time2 = str(item[16].strftime("%Y-%m-%d"))
                        self.logger.info("begin_time: {0}".format(begin_time2))
                        self.logger.info("end_time: {0}".format(end_time2))
                        assert item[11] == sku_price
                        assert item[12] == 1
                        assert begin_time2 == begin_time
                        assert end_time2 == end_time
                        assert item[17] == 0
                        assert item[19] == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_with_forever ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("没有登录下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_without_login(self):
        """ Test add visitor result interface add other without login."""
        self.logger.info(".... Start test_add_visitor_result_other_without_login ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid],"2010-2-4", "2038-02-11",self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客下单"):
                    httpclient1.update_header({"Cookie": ""})
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", time.strftime("%Y-%m-%d"), "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep10: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 1

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_without_login ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("本人没有下单下访客服务单")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_other_without_apply_user(self):
        """ Test add visitor result interface add other without apply user."""
        self.logger.info(".... Start test_add_visitor_result_other_without_apply_user ....")
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
                with allure.step("邀请访客下单"):
                    r_applyresult1 = h5_shopping_add_visitor_result(httpclient1, provider_id, spu_id, sku_id,
                           "kuli1", time.strftime("%Y-%m-%d"), "2021-02-10", "relate_face.jpg", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert not r_applyresult1

            with allure.step("teststep9: get visitor feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep10: get bus_service_order info"):
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert not select_result

            with allure.step("teststep11: get bus_order info"):
                table = 'bus_order'
                condition = ("member_id", self.member_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                assert len(select_result) == 0

            with allure.step("teststep12: user logout."):
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
            self.logger.info(".... End test_add_visitor_result_other_without_apply_user ....")
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
    def test_add_visitor_result_providerid_wrong(self, providerId, result):
        """ Test wrong providerId values (FT-HTJK-xxx-xxx).
        :param providerId: providerId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_providerid_wrong ({}) ....".format(providerId))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": providerId, "productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                            "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        allure.attach("request.body", str(rsp.request.body))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_providerid_wrong ({}) ....".format(providerId))
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
    def test_add_visitor_result_productid_wrong(self, productId, result):
        """ Test wrong productId values (FT-HTJK-xxx-xxx).
        :param productId: productId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_productid_wrong ({}) ....".format(productId))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": productId, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        allure.attach("request.body", str(rsp.request.body))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_productid_wrong ({}) ....".format(productId))
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
    def test_add_visitor_result_skuid_wrong(self, skuId, result):
        """ Test wrong skuId values (FT-HTJK-xxx-xxx).
        :param skuId: skuId parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_skuid_wrong ({}) ....".format(skuId))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": skuId, "visitor": "kuli1",
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        allure.attach("request.body", str(rsp.request.body))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                        self.logger.info("request.body: {}".format(rsp.request.body))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_skuid_wrong ({}) ....".format(skuId))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("visitor值")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("visitor, result",
                             [('1' * 51, {"status": 200, "code": '300', "msg": "访客姓名不能超过50个字符"}),
                              (1.5, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('a', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('中', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('*', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('1a', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('1中', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              ('%1%', {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (' ', {"status": 200, "code": '300', "msg": "姓名不能为空"}),
                              ('', {"status": 200, "code": '300', "msg": "姓名不能为空"}),
                              (11111, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (0, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (-1, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (9223372036854775808, {"status": 200, "code": '1', "msg": "提交邀请成功"}),
                              (-9223372036854775809, {"status": 200, "code": '1', "msg": "提交邀请成功"})],
                             ids=["visitor(超长值)", "visitor(小数)", "visitor(英文)", "visitor(中文)",
                                  "visitor(特殊字符)", "visitor(数字英文)", "visitor(数字中文)",
                                  "visitor(数字特殊字符)", "visitor(空格)", "visitor(空)",
                                  "visitor(1)", "visitor(0)", "visitor(-1)", "visitor(超大)", "visitor(超小)"])
    def test_add_visitor_result_visitor(self, visitor, result):
        """ Test wrong visitor values (FT-HTJK-xxx-xxx).
        :param visitor: visitor parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_visitor ({}) ....".format(visitor))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id, "visitor": visitor,
                                "beginTime": "2018-12-22", "endTime": "2022-09-08"}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_visitor ({}) ....".format(visitor))
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
                             ids=["beginTime(1.5)", "beginTime(1)", "beginTime(20000000000)", "beginTime(格式化)", "beginTime(英文)", "beginTime(中文)",
                                  "beginTime(特殊字符)", "beginTime(数字英文)", "beginTime(数字中文)",
                                  "beginTime(数字特殊字符)", "beginTime(空格)", "beginTime(空)",
                                  "beginTime(1)", "beginTime(0)", "beginTime(-1)", "beginTime(超大)", "beginTime(超小)"])
    def test_add_visitor_result_begintime_wrong(self, beginTime, result):
        """ Test wrong beginTime values (FT-HTJK-xxx-xxx).
        :param beginTime: beginTime parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_begintime_wrong ({}) ....".format(beginTime))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": beginTime, "endTime": '2025-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_begintime_wrong ({}) ....".format(beginTime))
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
    def test_add_visitor_result_endtime_wrong(self, endTime, result):
        """ Test wrong endTime values (FT-HTJK-xxx-xxx).
        :param endTime: endTime parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_endtime_wrong ({}) ....".format(endTime))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": '2030-01-01', "endTime": endTime}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_endtime_wrong ({}) ....".format(endTime))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("picture支持的图片类型")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("picture, result",
                             [("relate_face.png", {"status": 200, "code": "1", "msg": "提交邀请成功"}),
                              ("relate_face.jpg", {"status": 200, "code": "1", "msg": "提交邀请成功"}),
                              ("relate_face.jpeg", {"status": 200, "code": "1", "msg": "提交邀请成功"}),
                              ("relate_face.tif", {"status": 200, "code": "1", "msg": "提交邀请成功"}),
                              ("relate_face.bmp", {"status": 200, "code": "1", "msg": "提交邀请成功"}), ],
                             ids=["picture(png)", "picture(jpg)", "picture(jpeg)",
                                  "picture(tif)", "picture(bmp)"])
    def test_add_visitor_result_picture_correct(self, picture, result):
        """ Test correct picture values (FT-HTJK-xxx-xxx).
        :param picture: picture parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_picture_correct ({}) ....".format(picture))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path(picture), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_picture_correct ({}) ....".format(picture))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("picture不支持的文件类型")
    @allure.testcase("FT-HTJK-xxx-xxx")
    @pytest.mark.parametrize("picture, result",
                             [("relate_face.gif", {"status": 200, "code": "300", "msg": "照片不合格"}),
                              ("case.xlsx", {"status": 200, "code": "300", "msg": "照片不合格"}),
                              ("temp.txt", {"status": 200, "code": "300", "msg": "照片不合格"}),
                              ("hb.mp4", {"status": 200, "code": "300", "msg": "照片不合格"}),
                              ("fore1.PNG", {"status": 200, "code": "300", "msg": "照片不合格"}),
                              ("dog5.jpg", {"status": 200, "code": "300", "msg": "照片不合格"}), ],
                             ids=["picture(gif)", "picture(xlsx)", "picture(txt)",
                                  "picture(mp4)", "picture(other)", "picture(dog)"])
    def test_add_visitor_result_picture_wrong(self, picture, result):
        """ Test wrong picture values (FT-HTJK-xxx-xxx).
        :param picture: picture parameter value.
        :param result: expect result.
        """
        self.logger.info(".... Start test_add_visitor_result_picture_wrong ({}) ....".format(picture))
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path(picture), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
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
            self.logger.info(".... End test_add_visitor_result_picture_wrong ({}) ....".format(picture))
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少providerId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_providerid(self):
        """ Test add visitor result without providerid (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_providerid ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"productId": spu_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_providerid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少productId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_productid(self):
        """ Test add visitor result without productid (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_productid ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "skuId": sku_id, "visitor": "kuli1",
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_productid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少skuId参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_skuid(self):
        """ Test add visitor result without skuid (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_skuid ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "visitor": "kuli1",
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_skuid ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少visitor参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_visitor(self):
        """ Test add visitor result without visitor (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_visitor ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "beginTime": '2020-01-01', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_visitor ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少beginTime参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_begintime(self):
        """ Test add visitor result without beginTime (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_begintime ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "visitor": 'kuli1', "endTime": '2022-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_begintime ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少endTime参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_endtime(self):
        """ Test add visitor result without endTime (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_endtime ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "visitor": 'kuli1', "beginTime": '2020-01-01'}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data, files=files)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_endtime ....")
            self.logger.info("")

    @allure.severity("critical")
    @allure.story("缺少picture参数")
    @allure.testcase("FT-HTJK-xxx-xxx")
    def test_add_visitor_result_without_picture(self):
        """ Test add visitor result without picture (FT-HTJK-xxx-xxx)."""
        self.logger.info(".... Start test_add_visitor_result_without_picture ....")
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
                with allure.step("本人申请下单"):
                    r_applyresult1 = h5_shopping_apply_result(httpclient1, provider_id, spu_id, sku_id,
                                                              [owner_feautreid], "2010-2-4", "2038-02-11", self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1
                with allure.step("邀请访客"):
                    with allure.step("teststep: get parameters."):
                        data = {"providerId": provider_id, "productId": spu_id, "skuId": sku_id,
                                "visitor": 'kuli1', "beginTime": '2020-01-01', "endTime": "2022-01-01"}
                        files = {"picture": open(get_image_path("relate_face.jpg"), 'rb')}
                        allure.attach("params value", "{0}".format(data))
                        self.logger.info("data: {0}".format(data))
                    with allure.step("teststep: requests http get."):
                        rsp = httpclient1.post(self.URI, data=data)
                        allure.attach("request.headers", str(rsp.request.headers))
                        self.logger.info("request.url: {}".format(rsp.request.url))
                        self.logger.info("request.headers: {}".format(rsp.request.headers))
                    with allure.step("teststep: assert the response code"):
                        allure.attach("Expect response code：", '200')
                        allure.attach("Actual response code：", str(rsp.status_code))
                        self.logger.info("Actual response code：{0}".format(rsp.status_code))
                        assert rsp.status_code == 200
                        rsp_content = rsp.json()
                    with allure.step("teststep: assert the response content"):
                        allure.attach("response content：", str(rsp_content))
                        self.logger.info("response content: {}".format(rsp_content))
                        assert rsp_content["status"] == ''
                        assert "" in rsp_content["message"]

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
            self.logger.info(".... End test_add_visitor_result_without_picture ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_H5_Shopping_AddVisitorResult.py'])
    pytest.main(['-s', 'test_H5_Shopping_AddVisitorResult.py::TestShoppingAddVisitorResult::test_add_visitor_result_picture_wrong'])
