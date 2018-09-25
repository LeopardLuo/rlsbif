#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import hmac
import hashlib
import math


class Get_Param(object):

    def __init__(self, ProductKey, DeviceName, DeviceSecret, MqttServer='.iot-as-mqtt.cn-shanghai.aliyuncs.com'):
        self.ProductKey = ProductKey
        self.DeviceName = DeviceName
        self.DeviceSecret = DeviceSecret
        self.MqttHost = self.ProductKey + MqttServer

    def get_param(self):
        ProductKey = self.ProductKey
        ClientId = self.DeviceName
        DeviceName = self.DeviceName
        DeviceSecret = self.DeviceSecret
        hostname = self.MqttHost

        signmethod = "hmacsha1"
        us = math.modf(time.time())[1]
        ms = int(round(us * 1000))
        timestamp = str(ms)
        data = "".join(("clientId", ClientId, "deviceName", DeviceName,
                        "productKey", ProductKey, "timestamp", timestamp))

        password = hmac.new(bytes(DeviceSecret, encoding='utf-8'),
                       bytes(data, encoding='utf-8'),
                       hashlib.sha1).hexdigest()

        client_id = "".join((ClientId,
                             "|securemode=3",
                             ",signmethod=", signmethod,
                             ",timestamp=", timestamp,
                             "|"))
        username = "".join((DeviceName, "&", ProductKey))
        return client_id, username, password, hostname


if __name__ == '__main__':
    instance = Get_Param(ProductKey='YurProductKey', DeviceName='YourDeviceName', DeviceSecret='YourDeviceSecret')
    client_id, username, password, hostname = instance.get_param()
    print('client_id: ', client_id)
    print('username: ', username)
    print('password: ', password)
    print('Host name: ', hostname)
