#!/usr/bin/python
# -*-coding:utf-8-*-

import sys
import os
import pytest
from utils.ConfigParse import ConfigParse
from utils.MysqlClient import MysqlClient
from utils.LogTool import Logger


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
pPath = os.path.dirname(curPath)
ppPath = os.path.dirname(pPath)
sys.path.append(pPath)
print(pPath)

def cleardb():
    logger = Logger()
    logger.info("")
    logger.info("                 [**************** Start setupenv **************]")
    cp = ConfigParse()
    db_user = cp.getItem('db', 'db_user')
    db_password = cp.getItem('db', 'db_password')
    db_host = cp.getItem('db', 'db_host')
    db_database = cp.getItem('db', 'db_database')
    db_port = int(cp.getItem('db', 'db_port'))
    logger.info("db_user: {0}, db_password: {1}, db_host: {2}, db_database: {3}, "
                "db_port: {4}".format(db_user, db_password, db_host, db_database, db_port))
    mysql = MysqlClient(db_user, db_password, db_host, db_database, db_port)
    tables = ['bus_service_order', 'bus_service_order_device_list', 'bus_service_order_status', 'mem_features',
              'mem_member', 'mem_member_identity', 'mem_member_identity_other', 'mem_member_login', 'mem_order_record']
    for table in tables:
        delete_result = mysql.execute_delete_all(table)
        logger.info("delete table ({0}) result: {1}".format(table, delete_result))
    mysql.close()
    logger.info("                 [**************** End setupenv **************]")
    logger.info("")
    logger.close()


if __name__ == '__main__':
    os.system("del /s /q /f report\\*.txt")
    os.system("del /s /q /f report\\*.xml")
    # cleardb()
    pytest.main(['-s', 'testcases/', '-m=APP', '--alluredir', 'report'])
