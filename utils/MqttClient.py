#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import math
import time
import hmac
import queue

import paho.mqtt.client as mqtt
from paho.mqtt import publish
from paho.mqtt import subscribe


class AliParam(object):
    """ 封装阿里云物联网IOT连接参数的处理。

    :attribute __ProductKey: 阿里云物联网IOT注册产品的ProductKey。
    :attribute __DeviceName: 阿里云物联网IOT注册产品的设备的DeviceName。
    :attribute __DeviceSecret: 阿里云物联网IOT注册产品的设备的DeviceSecret。
    :attribute __MqttHost: 阿里云物联网IOT服务器主机。

    :Usage:
        >>> params = AliParam(ProductKey='a1GR7Y3uUvA', DeviceName='DName1', DeviceSecret='iXyZJV9GEIkBPekbiW6tQwJCYVTo3Iud')
        >>> clientid, username, password, hostname = params.get_param()
    """

    def __init__(self, ProductKey, DeviceName, DeviceSecret, MqttServer='.iot-as-mqtt.cn-shanghai.aliyuncs.com'):
        """ 初始化阿里云参数处理的基本参数。

        :param ProductKey: 阿里云的产品ProductKey。
        :param DeviceName: 阿里云IOT设备DeviceName。
        :param DeviceSecret: 阿里云IOT设备DeviceSecret。
        :param MqttServer: 阿里云IOT服务主机。
        """
        self.__ProductKey = ProductKey
        self.__DeviceName = DeviceName
        self.__DeviceSecret = DeviceSecret
        self.__MqttHost = self.__ProductKey + MqttServer

    def get_param(self):
        """ 获取经过阿里云IOT定义规则处理的参数值。
        :rtype: 返回处理后的clientid，username，password，hostname
        """
        ProductKey = self.__ProductKey
        ClientId = self.__DeviceName
        DeviceName = self.__DeviceName
        DeviceSecret = self.__DeviceSecret
        hostname = self.__MqttHost

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

class MqttClient(object):
    """ 对paho.mqtt包的模块client常用操作进行再封装，将订阅接收的消息放到队列进行缓冲处理。

    :attribute __host: IOT的MQTT服务器主机。
    :attribute __port: IOT的MQTT服务端口。
    :attribute __keepalive: IOT的MQTT服务保存连接时间。
    :attribute __rcv_msg: 订阅获取的消息队列。
    :attribute __client: MQTT连接的客户端。
    """

    def __init__(self, host, client_id='', username='', password=None, port=1883, keepalive=60, logger=None):
        """ 使用提供的参数值初始化MQTT客户端。

        :param host: MQTT服务主机。
        :param port: MQTT服务端口。
        :param client_id: MQTT服务连接使用的clientid，可选空，库自动生成唯一的id值。
        :param username: MQTT服务连接认证使用的用户名，可选。
        :param password: MQTT服务连接认证使用的密码，可选。
        :param keepalive: MQTT服务保持连接时间，默认值60秒。
        :param logger: 模块是否启用日志记录功能，如果提供日志处理器，则启用，不提供则关闭，默认关闭。
        """
        self.__host = host
        self.__port = port
        self.__keepalive = keepalive
        self.__rcv_msg = queue.Queue(100)
        self.__client = mqtt.Client(client_id)
        if logger:
            self.__client.enable_logger(logger)
        self.__client.username_pw_set(username, password)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_publish = self.__on_publish
        self.__client.on_subscribe = self.__on_subscribe
        self.__client.on_unsubscribe = self.__on_unsubscribe
        self.__client.connect(self.__host, self.__port, self.__keepalive)
        self.msgs = []

    @property
    def rcv_msg(self):
        """ 获取所有消息队列里面接收到的消息。
        :type: 接收的消息列表。
        """
        while not self.__rcv_msg.empty():
            self.msgs.append(self.__rcv_msg.get())
        return self.msgs

    def loopstart(self):
        """ 开始MQTT客户端接收消息的循环进程。"""
        self.__client.loop_start()

    def loopstop(self):
        """ 结束MQTT客户端接收消息的循环进程。"""
        self.__client.loop_stop()

    def publish(self, topic, payload=None, qos=0, retain=False):
        """ 发布MQTT消息。
        :param topic: 发布的MQTT消息主题。
        :param payload: 发布的MQTT消息内容，可选。
        :param qos: 发布的MQTT消息优先级，默认是0。
        :param retain: 服务端是否存储发布的MQTT消息，默认不存储。
        :rtype: None
        """
        self.__client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0):
        """ 订阅指定的主题消息。
        :param topic: 订阅的主题字符串。
        :param qos: 订阅主题的优先级0/1/2，默认是0。
        """
        self.__client.subscribe(topic)

    def unsubscribe(self, topic):
        """ 取消订阅指定的主题。
        :param topic: 要取消订阅的主题字符串。
        """
        self.__client.unsubscribe(topic)

    def clear(self):
        """  清空消息队列。"""
        while not self.__rcv_msg.empty():
            self.__rcv_msg.get()
        if self.msgs:
            self.msgs.clear()

    def close(self):
        """ 关闭MQTT客户端的连接。"""
        self.__client.disconnect()

    def __on_connect(self, client, userdata, flags, rc):
        """ 定义客户端连接的回调函数，客户端调用connect()函数后会调用此函数。
        :param client:      the client instance for this callback
        :param userdata:   the private user data as set in Client() or userdata_set()
        :param flags:      response flags sent by the broker
        :param rc:         the connection result

        flags is a dict that contains response flags from the broker:
            flags['session present'] - this flag is useful for clients that are
                using clean session set to 0 only. If a client with clean
                session=0, that reconnects to a broker that it has previously
                connected to, this flag indicates whether the broker still has the
                session information for the client. If 1, the session still exists.

        The value of rc indicates success or not:
            0: Connection successful
            1: Connection refused - incorrect protocol version
            2: Connection refused - invalid client identifier
            3: Connection refused - server unavailable
            4: Connection refused - bad username or password
            5: Connection refused - not authorised
            6-255: Currently unused.
        """
        print("Connected with result code: " + client.connack_string(rc))

    def __on_disconnect(self, client, userdata, rc):
        """ 定义客户端断开连接的回调函数，客户端调用disconnect()函数后会调用此函数。
        :param client:     the client instance for this callback
        :param userdata:   the private user data as set in Client() or userdata_set()
        :param rc:         the disconnection result
                    The rc parameter indicates the disconnection state. If
                    MQTT_ERR_SUCCESS (0), the callback was called in response to
                    a disconnect() call. If any other value the disconnection
                    was unexpected, such as might be caused by a network error.
        """
        print("Disconnected: " + str(rc))

    def __on_message(self, client, userdata, msg):
        """ 定义客户端接收到订阅的消息时，客户端会调用此函数。
        :param client:     the client instance for this callback
        :param userdata:   the private user data as set in Client() or userdata_set()
        :param msg:    an instance of MQTTMessage.
                    This is a class with members topic, payload, qos, retain.
        """
        if not self.__rcv_msg.full():
            self.__rcv_msg.put(msg)
        print("Received message '" + str(msg.payload) + "' on topic '"
              + msg.topic + "' with QoS " + str(msg.qos))
        print("userdata: " + str(userdata))

    def __on_publish(self, client, userdata, mid):
        """ 定义客户端发布消息的回调函数，客户端调用publish()函数后调用此函数。
        :param client:     the client instance for this callback
        :param userdata:   the private user data as set in Client() or userdata_set()
        :param mid:        matches the mid variable returned from the corresponding
                    publish() call, to allow outgoing messages to be tracked.
        """
        print("Publish message " + str(mid) + " sent.")

    def __on_subscribe(self,client, userdata, mid, granted_qos):
        """ 定义客户端订阅消息的回调函数，客户端调用subscribe()函数后调用此函数。
        :param client:         the client instance for this callback
        :param userdata:       the private user data as set in Client() or userdata_set()
        :param mid:            matches the mid variable returned from the corresponding
                        subscribe() call.
        :param granted_qos:    list of integers that give the QoS level the broker has
                        granted for each of the different subscription requests.
        """
        print("Subscribe: %s; qos: %s" % (str(mid), str(granted_qos)))

    def __on_unsubscribe(self, client, userdata, mid):
        """ 定义客户端取消订阅消息的回调函数，客户端调用unsubscribe()函数后调用此函数。
        :param client:     the client instance for this callback
        :param userdata:   the private user data as set in Client() or userdata_set()
        :param mid:        matches the mid variable returned from the corresponding
                    unsubscribe() call.
        """
        print("Unsubscribe: " + str(mid))

def publish_single(topic, payload=None, qos=0, retain=False, hostname="localhost",
    port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
    protocol=mqtt.MQTTv311, transport="tcp"):
    """ Publish a single message to a broker, then disconnect cleanly.
    publish_single("sensors/#", "sensor value", hostname="test.mosquitto.org")
    """
    publish.single(topic, payload=payload, qos=qos, retain=retain, hostname=hostname,
    port=port, client_id=client_id, keepalive=keepalive, will=will, auth=auth, tls=tls,
    protocol=protocol, transport=transport)

def publish_multiple(msgs, hostname="localhost", port=1883, client_id="", keepalive=60,
    will=None, auth=None, tls=None, protocol=mqtt.MQTTv311, transport="tcp"):
    """ Publish multiple messages to a broker, then disconnect cleanly.
    :param msgs: msg = {‘topic’:”<topic>”, ‘payload’:”<payload>”, ‘qos’:<qos>, ‘retain’:<retain>}
                or msg = (“<topic>”, “<payload>”, qos, retain)
    """
    publish.multiple(msgs, hostname=hostname, port=port, client_id=client_id, keepalive=keepalive,
    will=will, auth=auth, tls=tls, protocol=protocol, transport=transport)

def subscribe_simple(topics, qos=0, msg_count=1, retained=False, hostname="localhost",
    port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
    protocol=mqtt.MQTTv311):
    """ Subscribe to a set of topics and return the messages received. This is a blocking function.
    :param topics: the only required argument is the topic string to which the client will subscribe.
            This can either be a string or a list of strings if multiple topics should be subscribed to.
    :param msg_count: the number of messages to retrieve from the broker. Defaults to 1. If 1, a single
            MQTTMessage object will be returned. If >1, a list of MQTTMessages will be returned.
    :Exmaple:
        subscribe_simple("sensors/#", hostname="test.mosquitto.org")
    """
    return subscribe.simple(topics, qos=qos, msg_count=msg_count, retained=retained, hostname=hostname,
    port=port, client_id=client_id, keepalive=keepalive, will=will, auth=auth, tls=tls,
    protocol=protocol)

def subscribe_callback(callback, topics, qos=0, userdata=None, hostname="localhost",
    port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
    protocol=mqtt.MQTTv311):
    """ Subscribe to a set of topics and process the messages received using a user provided callback. """
    subscribe.callback(callback, topics, qos=qos, userdata=userdata, hostname=hostname,
    port=port, client_id=client_id, keepalive=keepalive, will=will, auth=auth, tls=tls,
    protocol=protocol)

def on_message_callback(client, userdata, message):
    print("Deal with the callback message here.")
    print(str(message))


if __name__ == '__main__':
    # client = MqttClient("iot.eclipse.org", 1883, 60)
    # client = MqttClient("test.mosquitto.org", 1883, 60)
    # client = MqttClient("broker.mqttdashboard.com", 1883, 60)
    # client.loopstart()
    # client.subscribe([("sensors/#", 2)])
    # client.publish("sensors/test", "Test MQTT", 2)
    # i = 0
    # while i < 20 and client.rcv_msg.empty():
    #     sleep(3)
    #     print("Wait times %d ." % i)
    #     i += 1
    # if not client.rcv_msg.empty():
    #     msg = client.rcv_msg.get()
    #     print("Received message '" + str(msg.payload) + "' on topic '"
    #           + msg.topic + "' with QoS " + str(msg.qos))
    # client.loopstop()
    # client.unsubscribe("sensors/#")
    # client.close()

    # publish_single("sensors/test", "Test MQTT", 2, hostname="broker.mqttdashboard.com")
    # msg = subscribe_simple("sensors/test", 2, 1, hostname="broker.mqttdashboard.com")
    # print("Received message '" + str(msg.payload) + "' on topic '"
    #           + msg.topic + "' with QoS " + str(msg.qos))

    # 阿里云使用例子
    params = AliParam(ProductKey='a1GR7Y3uUvA', DeviceName='DName1', DeviceSecret='iXyZJV9GEIkBPekbiW6tQwJCYVTo3Iud')
    clientid, username, password, hostname = params.get_param()
    # hostname = 'a1GR7Y3uUvA' + ".iot-as-mqtt.cn-shanghai.aliyuncs.com"
    authconfig = {'username': username, 'password': password}
    msg = subscribe_simple("/a1GR7Y3uUvA/DName1/update", 1, 1, client_id=clientid, hostname=hostname, port=1883, auth=authconfig)
    print("Received message '" + str(msg.payload) + "' on topic '"
          + msg.topic + "' with QoS " + str(msg.qos))
