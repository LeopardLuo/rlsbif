#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import time
import base64
import requests


def get_timestamp():
    return round(time.time())


def get_images(files, package_name='img'):
    """ 获取所有文件files的绝对路径，返回文件路径字符串列表。
    
    :param files: 文件名列表，如['img1.jpg', 'img2.bmp']
    :param package_name: 文件存放的包路径，如 'img'
    :rtype: 字符串列表
    """
    abs_files = []
    for file in files:
        root_path = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])
        file_path = os.path.join(root_path, package_name)
        abs_files.append(os.path.join(file_path, file))
    return abs_files


def encode_image(files):
    """ 使用base64编码方式对文件内容进行编码，返回编码后的列表，如果有文件不存在则返回空列表。

    :param files: 需要编码的文件绝对路径列表。
    :rtype: 文件编码后的列表。
    """
    b64_files = []
    for image_file in files:
        if os.path.exists(image_file):
            b64_files.append(base64.b64encode(open(image_file, 'rb').read()).decode())
        else:
            return []
    return b64_files


class HTTPClient(object):
    """ 封装的requests.session操作。
    
    :attribute __baseurl: 目标基本的url地址。
    :attribute __session: requests.Session对象。
    
    :usage:
        >>> client = HTTPClient('http://192.168.0.105:9088')
        >>> client.update_header({'PhoneSeri': 'Android123456'})
        >>> r = client.get('/api/Theme/GetTheme')
        >>> r.status_code
        200
        >>> client.close()
    """
    
    def __init__(self, baseurl):
        """ 使用基本的url参数初始化HTTPClient对象。
        
        :param baseurl: 目标基本url地址。
        """
        self.__baseurl = baseurl
        self.__session = requests.session()
        
    @property
    def baseurl(self):
        """ 获取当前基本的目标url地址。"""
        return self.__baseurl
    
    @baseurl.setter
    def baseurl(self, value):
        """ 设置当前基本的目标url地址。
        
        :param value: 新的url地址字符串。
        """
        self.__baseurl = value
        
    def close(self):
        """ 关闭当前打开的requests.session连接。"""
        self.__session.close()
        
    def set_auth(self, user, password):
        """ 设置认证的用户密码。其实就是header里面的authentication。"""
        self.__session.auth = (user, password)
        
    def update_header(self, headers):
        """ 增加HTTP header的内容，如果要删除字段就设置相应的字段内容为None。"""
        self.__session.headers.update(headers)
    
    def get(self, uri, data=None, headers=None):
        """ 实现requests.get功能。
        
        :param uri: GET请求的uri，不包括主机名和端口，如/api/Theme/GetTheme
        :param data: GET请求url上面的参数配置， dict类型，可选。
        :param headers: GET请求的HTTP头的配置，dict类型，可选。
        
        :rtype: response对象。
        """
        url = self.__baseurl + uri
        print(url)
        return self.__session.get(url, data=data, headers=headers)
#         status_code = rsp.status_code
#         rsp_data = rsp.json()
#         rsp_header = rsp.headers
#         request_header = rsp.request.headers
#         request_body = rsp.request.body.decode()
    
    def post(self, uri, data=None, json=None, files=None, headers=None):
        """ 实现requests.post功能。
        
        :param uri: POST请求的uri，不包括主机名和端口，如/api/Theme/GetTheme
        :param data: POST请求的form表参数，dict类型，可选。
        :param json: POST请求的json格式参数，dict类型，可选。
        :param files: POST请求的multi/form-data的附件文件，list类型，可选。
        :param headers: POST请求的HTTP头的配置，dict类型，可选。
        
        :rtype: response对象。
        """
        url = self.__baseurl + uri
        return self.__session.post(url, data, json, files=files, headers=headers)
    

if __name__ == "__main__":
    files = get_images(['Kaola.jpg'])
    print(files)
    print(encode_image(files))
    
    # print("\n start")
    # client = HTTPClient('http://192.168.0.105:9088')
    # client.update_header({'PhoneSeri': 'Android123456'})
    # r = client.get('/api/Theme/GetTheme')
    # print(r.status_code)
    # client.close()

    print(get_timestamp())
