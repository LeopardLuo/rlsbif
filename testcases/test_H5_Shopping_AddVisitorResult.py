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
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == features_id1
                assert select_result[0][7] == 'kuli1'
                assert select_result[0][8] == 99
                assert select_result[0][9] == 0
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
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == features_id1
                assert select_result[0][7] == 'kuli1'
                assert select_result[0][8] == 99
                assert select_result[0][9] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

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
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == features_id1
                assert select_result[0][7] == 'kuli1'
                assert select_result[0][8] == 99
                assert select_result[0][9] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

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
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == features_id1
                assert select_result[0][7] == 'kuli1'
                assert select_result[0][8] == 99
                assert select_result[0][9] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

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
                table = 'bus_service_order'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "kuli1"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                service_order_id = select_result[0][0]
                begin_time = str(datetime.datetime.fromtimestamp(select_result[0][13])).split(" ")[0]
                end_time = str(datetime.datetime.fromtimestamp(select_result[0][14])).split(" ")[0]
                self.logger.info("service_order_id: {0}".format(service_order_id))
                self.logger.info("begin_time: {0}".format(begin_time))
                self.logger.info("end_time: {0}".format(end_time))
                assert select_result[0][2] == provider_name
                assert select_result[0][6] == features_id1
                assert select_result[0][7] == 'kuli1'
                assert select_result[0][8] == 99
                assert select_result[0][9] == 0
                assert begin_time == "2014-06-21"
                assert end_time == "2021-02-10"
                assert select_result[0][15] == 0
                assert select_result[0][16] == 1

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


if __name__ == '__main__':
    pytest.main(['-s', 'test_H5_Shopping_AddVisitorResult.py'])
    # pytest.main(['-s', 'test_H5_Shopping_AddVisitorResult.py::TestShoppingAddVisitorResult::test_add_visitor_result_other_with_forever'])
