# -*-coding:utf-8-*-
import paho.mqtt.client as mqtt
from Mqtt_Client import *

# # 当连接上服务器后回调此函数
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#
#     # 放在on_connect函数里意味着
#     # 重新连接时订阅主题将会被更新
#     client.subscribe("topic/sub")
#
#
# # 从服务器接受到消息后回调此函数
# def on_message(client, userdata, msg):
#     print("主题:" + msg.topic + " 消息:" + str(msg.payload))
#
#
# client = mqtt.Client()
# # 参数有 Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
# client.on_connect = on_connect  # 设置连接上服务器回调函数
# client.on_message = on_message  # 设置接收到服务器消息回调函数
# client.connect("iot.eclipse.org", 1883, 60)  # 连接服务器,端口为1883,维持心跳为60秒
# client.loop_forever()

# publish_single("sensors/test", "Test MQTT", 2, hostname="broker.mqttdashboard.com")

# 阿里云发布消息
params = Get_Param(ProductKey='a1GR7Y3uUvA', DeviceName='DName2', DeviceSecret='RRySeuQ1tZ16bvNDEYIgWmtHrmaU7Uh9')
clientid, username, passoword = params.get_param()
hostname = 'a1GR7Y3uUvA' + ".iot-as-mqtt.cn-shanghai.aliyuncs.com"
authconfig = {'username': username, 'password': passoword}
# publish_single('/a1GR7Y3uUvA/DName2/update', 'Test Message!', 1, hostname=hostname, client_id=clientid, auth=authconfig)


client = MqttClient(hostname, 1883, clientid, username, passoword)
for i in range(5):
    client.publish('/a1GR7Y3uUvA/DName2/update', 'Test Message!', 1)
    print(i)
    sleep(10)
client.close()
