#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import re
import configparser
from configparser import NoOptionError, NoSectionError


class ConfigParse(object):
    """ ConfigParse类封装了对配置文件的基本操作
    
    .封装的功能包括获取section所有配置项，删除section，插入一个配置项，获取一个配置项，删除一个配置项。
    
    Attributes:
        __parser: configparser实例，用于操作配置文件。
        __configfile: 配置文件的完整名称，包括路径，用于指定配置文件。
    """
    
    def __init__(self, configs=None, filename='config.ini'):
        """ 初始化配置文件config/filename，如果文件不存在就创建配置文件，如果提供configs配置，则将configs配置插入配置文件。
        
        Args:
            configs: 初始化时需要增加的配置字典，配置可以是一个或者多个，默认值是None。
            filename: 初始化指定的配置文件名字，默认值是'config.ini'。
        Examples:
            configs = {
                'db2': {
                    'db_user': 'root',
                    'db_password': 'hrst123',
                    'db_database': 'gdhdb',
                    'db_host': '192.168.0.106',
                    'db_port': '3306'
                    }
                }
        """
        if re.match(r'.*src$', os.getcwd()):
            configpath = os.path.join(os.getcwd(), 'config')
        else:
            configpath = os.path.join(os.path.dirname(os.getcwd()), 'config')
        self.__configfile = os.path.join(configpath, filename)
        if not os.path.exists(configpath):
            os.makedirs(configpath)
        if not os.path.exists(self.__configfile):
            fh = open(self.__configfile, 'w')
            fh.close()
        
        self.__parser = configparser.ConfigParser()
        self.__parser.read(self.__configfile)
        if configs:
            for s in configs.keys():
                self.__parser.add_section(s)
                for k, v in configs[s].items():
                    self.__parser.set(s, k, str(v))
            self.saveFile()
                
    def saveFile(self):
        """ 将配置数据保存回配置文件"""
        with open(self.__configfile, 'w') as fh:
                self.__parser.write(fh)
    
    def getSection(self, section):
        """ 获取section里面的所有配置项。
        
        Args:
            section: 要获取的区域字符串，如 ('db')
        
        Returns:
            section里面所有配置项的字典，如果section值不存在，则返回空字典{}。
            example:
            {'db_user': 'root', 'db_password': 'hrst123', 'db_database': 'gdhdb', 'db_host': '192.168.0.105', 'db_port': '3306'}
        """
        self.__parser.read(self.__configfile)
        try:
            if not self.__parser.has_section(section):
                return {}
            items = self.__parser.items(section)
            return dict(items)
        except NoSectionError as err:
            print(err)
            return {}
    
    def getItem(self, section, key):
        """ 获取section里面的配置项key的值。
        
        Args:
            section: 要获取配置的区域字符串，如 ('db')
            key: 要获取的配置关键字字符串，如('db_host')
        
        Returns:
            section里面的配置项key对应的值字符串，如果section或者key不存在，则返回空对象None。
            .所有返回值都是字符串，如果需要其他的类型，则需要自己处理返回值得类型转换，如int(value)。
        """
        self.__parser.read(self.__configfile)
        try:
            if self.__parser.has_option(section, key):
                return self.__parser.get(section, key)
            else:
                return None
        except NoOptionError as err:
            print(err)
            return None
    
    def addItem(self, section, key, value):
        """ 将section的配置项key = value增加到配置文件。
        
        .如果section不存在，会自动增加一个section，如果section里面已经存在配置项key，则先删除原来的配置项，重新增加。
        
        Args:
            section: 要增加配置的区域字符串，如 ('db')。
            key: 要增加的配置关键字字符串，如('db_host')。
            value: 要增加的配置项值字符串，如('192.168.0.105')。
        """
        self.__parser.read(self.__configfile)
        if not self.__parser.has_section(section):
            self.__parser.add_section(section)
        if self.__parser.has_option(section, key):
            self.__parser.remove_option(section, key)
        self.__parser.set(section, key, value)
        self.saveFile()
    
    def delSection(self, section):
        """ 删除section以及里面的所有配置项。
        
        Args:
            section: 要删除配置的区域字符串，如 ('db')。
        """
        self.__parser.read(self.__configfile)
        if not self.__parser.has_section(section):
            return
        self.__parser.remove_section(section)
    
    def delItem(self, section, key):
        """ 删除section里面的一个配置项key。
        
        Args:
            section: 要删除配置的区域字符串，如 ('db')。
            key: 要删除的配置关键字字符串，如('db_host')。
        """
        self.__parser.read(self.__configfile)
        if not self.__parser.has_section(section):
            return
        if not self.__parser.has_option(section, key):
            return
        self.__parser.remove_option(section, key)

    
if __name__ == "__main__":
#     default_config = {'db2': {
#         'db_user': 'root',
#         'db_password': 'hrst123',
#         'db_database': 'gdhdb',
#         'db_host': '192.168.0.106',
#         'db_port': '3306'}}
#     cp = ConfigParse(default_config)
#     cf = cp.getSection('db')
#     print(cf)
    cp = ConfigParse()
    print(cp.getSection('db'))
#     v = cp.getItem('db', 'db_port')
#     print(v)
#     cp.delItem('db2', 'comment')
#     cp.addItem('db2', 'comment', 'test')
#     print(cp.getItem('db2', 'comment'))
    