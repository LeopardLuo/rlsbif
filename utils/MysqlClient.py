#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import mysql.connector
from utils.ConfigParse import ConfigParse


class MysqlClient(object):
    """ MysqlClient类封装了对Mysql数据库的基本操作，包括插入表数据，查询表数据，删除表数据。
    
    Attributes:
        __cnx: mysql数据库连接的对象。
        __cursor: mysql数据库操作的游标对象。
    """

    def __init__(self, user, password, host, database=None, port=3306):
        """ 使用给定参数初始化mysql数据库连接，并且获取操作的游标。
        
        Args:
            user: 建立数据库连接的用户名字符串。
            password: 建立数据库连接的用户登录密码字符串。
            host: 建立数据库连接的数据库主机字符串，可以是域名或者ip地址。
            database: 建立连接使用的目标数据库名字符串，默认是None。
            port: 建立数据库连接时的主机端口号，int类型，默认是3306.
        """
        self.__cnx = mysql.connector.connect(user=user, password=password, host=host, database=database, port=port)
        self.__cursor = self.__cnx.cursor()
        
    def create_database(self, db_name):
        """ 创建数据库db_name，使用时初始化连接数据库不能指定database，否则无法创建。
        
        Args:
            db_name: 要创建的数据库名字字符串。
        """
        try:
            self.__cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)
        
    def create_table(self, table_config):
        """ 创建数据库表table_config。
        
        Args:
            table_config: 完整的mysql创建数据库表的sql语句。
        
        Example:
            create_table = '''CREATE TABLE IF NOT EXISTS employees (
                        emp_no int(11) NOT NULL AUTO_INCREMENT,
                        birth_date date NOT NULL,
                        first_name varchar(14) NOT NULL,
                        last_name varchar(16) NOT NULL,
                        gender enum("M", "F") NOT NULL,
                        hire_date date NOT NULL,
                        PRIMARY KEY (emp_no)
                    ) ENGINE=InnoDB'''
        """
        try:
            self.__cursor.execute(table_config)
        except mysql.connector.Error as err:
            print("Failed creating table: {}".format(err))
            exit(1)
    
    def execute_insert(self, table, datas):
        """ 向指定的数据库表table插入数据datas，插入过程是一个事务，中间如果有异常错误，则回滚整个事务。
        
        Args:
            table: 要插入数据的目标数据库表名字符串。
            datas: 需要插入的数据字典列表，一个字典相当于一条表数据，字典的key是表的字段名字符串，字典的value是插入相应字段的值。
            
        Example:
            datas = [{'birth_date': '2010-1-10', 'first_name': 'Jimmy', 'last_name': 'Cal', 'gender': 'F', 'hire_date': '2018-9-10'},
                    {'birth_date': '2010-2-10', 'first_name': 'Bob', 'last_name': 'TT', 'gender': 'M', 'hire_date': '2018-10-10'}]
        
        Returns:
            .删除记录成功返回True，删除有异常或者出错返回False。
        """
        try:
            for data in datas:
                keys = data.keys()
                values = ["'{}'".format(data[k]) for k in keys]
                sql = """INSERT INTO {0} ({1}) VALUES ({2})""".format(table, ','.join(keys), ",".join(values))
                self.__cursor.execute(sql)
            self.__cnx.commit()
            return True
        except mysql.connector.Error as err:
            print("Failed to execute insert SQL: {}".format(err))
            self.__cnx.rollback()
            return False
    
    def execute_select_all(self, table):
        """ 查询数据库表table的所有记录。
        
        Args:
            table: 要查询的数据库表名字符串。
            
        Returns:
            .所有数据库表记录的列表，其中每个记录又是一个列表，相当于是一个二维数组，如果有异常或者错误则返回None。
        """
        try:
            sql = "SELECT * FROM %s" % (table)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
            self.__cnx.commit()
            return result
        except mysql.connector.Error as err:
            print("Failed to execute SQL: {}".format(err))
            return None
    
    def execute_delete_all(self, table):
        """ 删除数据库表table的所有记录。
        
        Args:
            table: 要清除的数据库表名字符串。
        
        Returns:
            .删除记录成功返回True，删除有异常或者出错返回False。
        """
        try:
            sql = "DELETE FROM " + table
            self.__cursor.execute(sql)
            self.__cnx.commit()
            return True
        except mysql.connector.Error as err:
            print("Failed to delete table: {}".format(err))
            self.__cnx.rollback()
            return False
    
    def execute_select_condition(self, table, condition):
        """ 查询数据库表table符合条件condition的记录，使用的是where子句的查询条件。
        
        Args:
            table: 要查询的数据库表名字符串。
            condition: 一个tuple查询条件，第一个元素是字段名，第二个元素是字段的值，用于where子句中的'字段名=值'。
            
        Returns:
            .符合条件的所有数据库表记录列表，其中每个记录又是一个列表，相当于是一个二维数组，如果有异常或者错误则返回None。
        """
        try:
            cd = "%s='%s'" % (condition[0], condition[1])
            sql = "SELECT * FROM {0} WHERE {1}".format(table, cd)
            print(sql)
            self.__cursor.execute(sql)
            result = list(self.__cursor.fetchall())
            self.__cnx.commit()
            return result
        except mysql.connector.Error as err:
            print("Failed to select table: {}".format(err))
            return None
    
    def execute_delete_condition(self, table, condition):
        """ 删除数据库表table中符合条件condition的记录，使用的是where子句的删除条件。
        
        Args:
            table: 要删除记录的数据库表名字符串。
            condition: 一个tuple查询条件，第一个元素是字段名，第二个元素是字段的值，用于where子句中的'字段名=值'。
            
        Returns:
            .删除记录成功返回True，删除有异常或者出错返回False。
        """
        try:
            cd = "%s like '%s'" % (condition[0], condition[1])
            sql = "DELETE FROM {0} WHERE {1}".format(table, cd)
            self.__cursor.execute(sql)
            self.__cnx.commit()
            return True
        except mysql.connector.Error as err:
            print("Failed to delete record: {}".format(err))
            return False
    
    def close(self):
        """ 关闭数据库打开的游标和连接实例。"""
        self.__cursor.close()
        self.__cnx.close()


if __name__ == '__main__':
    cp = ConfigParse()
    db = cp.getSection('db2')
    client = MysqlClient(db['db_user'], db['db_password'], db['db_host'], db['db_database'])
#     client.create_database('test')
#     create_table = """CREATE TABLE IF NOT EXISTS employees (
#                         emp_no int(11) NOT NULL AUTO_INCREMENT,
#                         birth_date date NOT NULL,
#                         first_name varchar(14) NOT NULL,
#                         last_name varchar(16) NOT NULL,
#                         gender enum('M', 'F') NOT NULL,
#                         hire_date date NOT NULL,
#                         PRIMARY KEY (emp_no)
#                     ) ENGINE=InnoDB"""
#     client.create_table(create_table)
    
    table = 'employees'
    datas = [{'birth_date': '2010-1-10', 'first_name': 'Jimmy', 'last_name': 'Cal', 'gender': 'F', 'hire_date': '2018-9-10'}]
    client.execute_insert(table, datas)
    
    resultset = client.execute_select_condition(table, ('first_name', 'Jimmy'))
    print(resultset)
    
    client.execute_delete_all(table)
    
    resultset = client.execute_select_all(table)
    print(resultset)
    client.close()
    
    print(round(time.time()))