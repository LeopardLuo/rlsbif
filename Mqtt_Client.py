#!/usr/bin/env python
# -*- coding:utf-8 -*-

from time import sleep
import paho.mqtt.client as mqtt
from paho.mqtt import publish
from paho.mqtt import subscribe
import queue

from Get_Param import Get_Param


class MqttClient(object):
    """ 对paho.mqtt包的模块client常用操作进行再封装，将订阅接收的消息放到队列进行缓冲处理。 """

    def __init__(self, host, port=1883, client_id='', username='', password=None, keepalive=60, logger=None):
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self.__rcv_msg = queue.Queue(100)
        self.client = mqtt.Client(client_id)
        if logger:
            self.client.enable_logger(logger)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_publish = self.__on_publish
        self.client.on_subscribe = self.__on_subscribe
        self.client.on_unsubscribe = self.__on_unsubscribe
        self.client.connect(self.host, self.port, self.keepalive)

    @property
    def rcv_msg(self):
        return self.__rcv_msg

    def loopstart(self):
        self.client.loop_start()

    def loopstop(self):
        self.client.loop_stop()

    def publish(self, topic, payload=None, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topics):
        self.client.subscribe(topics)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)

    def close(self):
        self.client.disconnect()

    def __on_connect(self, client, userdata, flags, rc):
        print("Connected with result code: " + client.connack_string(rc))

    def __on_disconnect(self, client, userdata, rc):
        print("Disconnected: " + str(rc))

    def __on_message(self, client, userdata, msg):
        if not self.__rcv_msg.full():
            self.__rcv_msg.put(msg)
        print("Received message '" + str(msg.payload) + "' on topic '"
              + msg.topic + "' with QoS " + str(msg.qos))
        print("userdata: " + str(userdata))

    def __on_publish(self, client, userdata, mid):
        print("Publish message " + str(mid) + " sent.")

    def __on_subscribe(self,client, userdata, mid, granted_qos):
        print("Subscribe: %s; qos: %s" % (str(mid), str(granted_qos)))

    def __on_unsubscribe(self, client, userdata, mid):
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
    @:param msgs: msg = {‘topic’:”<topic>”, ‘payload’:”<payload>”, ‘qos’:<qos>, ‘retain’:<retain>}
                or msg = (“<topic>”, “<payload>”, qos, retain)
    """
    publish.multiple(msgs, hostname=hostname, port=port, client_id=client_id, keepalive=keepalive,
    will=will, auth=auth, tls=tls, protocol=protocol, transport=transport)

def subscribe_simple(topics, qos=0, msg_count=1, retained=False, hostname="localhost",
    port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
    protocol=mqtt.MQTTv311):
    """ Subscribe to a set of topics and return the messages received. This is a blocking function. 
    @:param topics: the only required argument is the topic string to which the client will subscribe. 
            This can either be a string or a list of strings if multiple topics should be subscribed to.
    @:param msg_count: the number of messages to retrieve from the broker. Defaults to 1. If 1, a single
            MQTTMessage object will be returned. If >1, a list of MQTTMessages will be returned.
    @:Exmaple:
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
    params = Get_Param(ProductKey='a1GR7Y3uUvA', DeviceName='DName1', DeviceSecret='iXyZJV9GEIkBPekbiW6tQwJCYVTo3Iud')
    clientid, username, password, hostname = params.get_param()
    # hostname = 'a1GR7Y3uUvA' + ".iot-as-mqtt.cn-shanghai.aliyuncs.com"
    authconfig = {'username': username, 'password': password}
    msg = subscribe_simple("/a1GR7Y3uUvA/DName1/update", 1, 1, client_id=clientid, hostname=hostname, port=1883, auth=authconfig)
    print("Received message '" + str(msg.payload) + "' on topic '"
          + msg.topic + "' with QoS " + str(msg.qos))
