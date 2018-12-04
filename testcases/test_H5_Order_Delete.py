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

@pytest.mark.H5
@allure.feature("H5-删除服务单")
class TestOrderDelete(object):

    @allure.step("+++ setup class +++")
    def setup_class(cls):
        cls.logger = Logger()

        cls.logger.info("")
        cls.logger.info("*** Start setup class ***")
        try:
            with allure.step("初始化配置文件对象。"):
                cls.config = ConfigParse()
            with allure.step("获取测试URI值。"):
                cls.URI = cls.config.getItem('uri', 'H5OrderDelete')
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

    def test_delete_add_member_other_order(self):
        """ Test order delete interface delete add memeber other order. """
        self.logger.info(".... Start test_delete_add_member_other_order ....")
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

            with allure.step("teststep4: identity relative."):
                identity_result1 = identity_other(self.httpclient, self.member_id, 'kuli1', 'relate_face.jpg',
                                                  'face2.jpg', get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result1))
                self.logger.info("identity relative result: {0}".format(identity_result1))
                identity_result2 = identity_other(self.httpclient, self.member_id, 'mm1', 'mm1.jpg',
                                                  'face2.jpg',
                                                  get_timestamp(), self.logger)
                allure.attach("identity relative result", "{0}".format(identity_result2))
                self.logger.info("identity relative result: {0}".format(identity_result2))

            with allure.step("teststep5: get provider id"):
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

            with allure.step("teststep6: get spu id"):
                table = 'bus_spu'
                condition = ("provider_id", provider_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                spu_id = select_result[0][0]

            with allure.step("teststep7: get sku id"):
                table = 'bus_sku'
                condition = ("spu_id", spu_id)
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_condition(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                sku_id = select_result[0][0]

            with allure.step("teststep8: get owner feature"):
                table = 'mem_features'
                condition = ("member_id = '{}' and features_name = '{}'".format(self.member_id, "本人"))
                allure.attach("table name and condition", "{0},{1}".format(table, condition))
                self.logger.info("")
                self.logger.info("table: {0}, condition: {1}".format(table, condition))
                select_result = self.mysql.execute_select_conditions(table, condition)
                allure.attach("query result", str(select_result))
                self.logger.info("query result: {0}".format(select_result))
                owner_feautreid = select_result[0][0]

            with allure.step("teststep9: get features id by user info."):
                user_info = get_identity_other_list(self.httpclient, self.member_id, 0, 10, get_timestamp(),
                                                    logger=self.logger)
                allure.attach("features data list", "{0}".format(user_info))
                self.logger.info("features data list: {0}".format(user_info))
                features_id1 = user_info[0]['features_id']
                features_id2 = user_info[1]['features_id']

            with allure.step("teststep10: create service orders"):
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
                with allure.step("本人申请成员下单"):
                    r_applyresult1 = h5_shopping_add_member_result(httpclient1, provider_id, spu_id, sku_id,
                                                                   [features_id1, features_id2], self.logger)
                    allure.attach("apply result", str(r_applyresult1))
                    self.logger.info("apply result: " + str(r_applyresult1))
                    assert r_applyresult1

            with allure.step("teststep11: get service order list."):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                assert len(r_order) == 3

            with allure.step("teststep12: delete order."):
                for data in r_order:
                    service_order_id = data['service_order_id']
                    table = 'bus_order'
                    condition = ("service_order_id", service_order_id)
                    allure.attach("table name and condition", "{0},{1}".format(table, condition))
                    self.logger.info("")
                    self.logger.info("table: {0}, condition: {1}".format(table, condition))
                    select_result = self.mysql.execute_select_condition(table, condition)
                    allure.attach("query result", str(select_result))
                    self.logger.info("query result: {0}".format(select_result))
                    order_id = select_result[0][0]
                    close_state = h5_order_delete(httpclient1, provider_id, spu_id, sku_id, order_id,
                                                  self.logger)
                    assert close_state

            with allure.step("teststep13: get service order list."):
                r_order = get_myservice_order_list(self.httpclient, self.member_id, 0, 10, 3, timestamp=get_timestamp(),
                                                   logger=self.logger)
                allure.attach("service order list", str(r_order))
                self.logger.info("service order list: {0}".format(r_order))
                for data in r_order:
                    assert data['state'] == 2

            with allure.step("teststep14: user logout."):
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
            self.logger.info(".... End test_delete_add_member_other_order ....")
            self.logger.info("")


if __name__ == '__main__':
    # pytest.main(['-s', 'test_H5_Order_Delete.py'])
    pytest.main(['-s', 'test_H5_Order_Delete.py::TestOrderDelete::test_delete_add_member_other_order'])
