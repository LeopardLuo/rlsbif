#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
from time import sleep
from queue import Queue
import threading
import allure

from utils.HTTPClient import *
from utils.ConfigParse import ConfigParse
from utils.MqttClient import *
from utils.CommonTool import *


@allure.step("Register-GetMsgCode")
def get_msg_code(httpclient, code_type, phone, timestamp=None, logger=None):
    """ Register GetMsgCode interface, return code_token value or blank.
    :param httpclient: http request client.
    :param code_type: interface defined paramter code_type int type.
    :param phone: interface defined parameter phone string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: code_token string or blank string.
    """
    logger and logger.info("")
    logger and logger.info("---- start get_msg_code ----")
    uri = ConfigParse().getItem("uri", "GetMsgCode")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"code_type": code_type, "phone": phone, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("GetMsgCode json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body.decode()))
    logger and logger.info("request.body: {}".format(rsp.request.body.decode()))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("~~~~ start get_msg_code ~~~~")
        logger and logger.info("")
        return ""
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end get_msg_code ----")
    logger and logger.info("")
    if rsp_content["code"] == 1 and rsp_content["result"]["code_token"]:
        return rsp_content["result"]["code_token"]
    else:
        return ""


@allure.step("Register-Apply")
def register(httpclient, client_type, client_version, device_token, imei, phone, code_token, sms_code, timestamp=None, token="", logger=None):
    """ Register interface, return True or False.
    :param httpclient: http request client.
    :param client_type: interface defined paramter client_type int type.
    :param client_version: interface defined parameter client_version string type.
    :param device_token: interface defined parameter device_token string type.
    :param imei: interface defined parameter client phone imei string type.
    :param phone: interface defined parameter register phone number string type.
    :param code_token: interface GetMsgCode return code_token string type.
    :param sms_code: run interface GetMsgCode get from phone sms code string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param token: get from webchat platform login authentication token, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result dict register successfully, {} register failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start register ----")
    uri = ConfigParse().getItem("uri", "Register")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"client_type": client_type, "client_version": client_version, "device_token": device_token, "imei": imei,
            "phone": phone, "code_token": code_token, "sms_code": sms_code, "timestamp": timestamp, "token": token}
    allure.attach("request params", str(json))
    logger and logger.info("Register json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body.decode()))
    logger and logger.info("request.body: {}".format(rsp.request.body.decode()))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("~~~~ start register ~~~~")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end register ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-AppLogin")
def app_login(httpclient, client_type, client_version, device_token, imei, phone, sms_code, code_token, timestamp=None, logger=None):
    """ APP login interface, return login user info dict.
    :param httpclient: http request client.
    :param client_type: interface defined paramter client_type int type.
    :param client_version: interface defined parameter client_version string type.
    :param device_token: interface defined parameter device_token string type.
    :param imei: interface defined parameter client phone imei string type.
    :param phone: interface defined parameter register phone number string type.
    :param code_token: interface GetMsgCode return code_token string type.
    :param sms_code: run interface GetMsgCode get from phone sms code string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result dict login successfully, {} login failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start app_login ----")
    uri = ConfigParse().getItem("uri", "AppLogin")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"client_type": client_type, "client_version": client_version, "device_token": device_token, "imei": imei,
            "phone": phone, "code_token": code_token, "sms_code": sms_code, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("App Login json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body.decode()))
    logger and logger.info("request.body: {}".format(rsp.request.body.decode()))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end app_login ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end app_login ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-WXLogin")
def wx_login(httpclient, client_type, client_version, device_token, imei, code, timestamp=None, logger=None):
    """ webchat login interface, return login user info dict.
    :param httpclient: http request client.
    :param client_type: interface defined paramter client_type int type.
    :param client_version: interface defined parameter client_version string type.
    :param device_token: interface defined parameter device_token string type.
    :param imei: interface defined parameter client phone imei string type.
    :param code: webchat return code string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result dict login successfully, {} login failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start wx_login ----")
    uri = ConfigParse().getItem("uri", "WXLogin")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"client_type": client_type, "client_version": client_version, "device_token": device_token, "imei": imei,
            "code": code, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("webchat Login json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body.decode()))
    logger and logger.info("request.body: {}".format(rsp.request.body.decode()))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end wx_login ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end wx_login ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-Logout")
def logout(httpclient, member_id, timestamp=None, logger=None):
    """ User logout interface, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result True logout successfully, False logout failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start logout ----")
    uri = ConfigParse().getItem("uri", "Logout")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("Logout json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body.decode()))
    logger and logger.info("request.body: {}".format(rsp.request.body.decode()))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end logout ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end logout ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-InfoList")
def userinfo(httpclient, member_id, timestamp=None, logger=None):
    """ Get user info interface, return user info dict or blank.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return user info dict successfully, {} when failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start userinfo ----")
    uri = ConfigParse().getItem("uri", "UserInfo")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"member_id": member_id, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("UserInfo json: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end userinfo ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end userinfo ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-ModifyNickName")
def modify_nick_name(httpclient, member_id, nickname, timestamp=None, logger=None):
    """ Modify nick name of user info, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param nickname: interface defined parameter nickname string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result True logout successfully, False logout failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_nick_name ----")
    uri = ConfigParse().getItem("uri", "ModifyNickName")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "nickname": nickname, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifyNickName json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_nick_name ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_nick_name ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-ModifySex")
def modify_sex(httpclient, member_id, sex, timestamp=None, logger=None):
    """ Modify nick name of user info, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param sex: interface defined parameter sex int type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result True logout successfully, False logout failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_sex ----")
    uri = ConfigParse().getItem("uri", "ModifySex")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "sex": sex, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifySex json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_sex ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_sex ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-ModifyHeadImage")
def modify_head_image(httpclient, member_id, head_image, timestamp=None, logger=None):
    """ Modify head image of user info, return new image url or blank.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param head_image: interface defined parameter head_image base64 encode type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: result new image url dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_head_image ----")
    uri = ConfigParse().getItem("uri", "ModifyHeadImage")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "head_image": head_image, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifyHeadImage json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_head_image ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_head_image ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-ModifyHomeAddress")
def modify_home_address(httpclient, member_id, province, city, district, address, timestamp=None, logger=None):
    """ Modify home address of user info, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param province: interface defined parameter province string type.
    :param city: interface defined parameter city string type.
    :param district: interface defined parameter district string type.
    :param address: interface defined parameter address string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True modify successfully, False modify failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_home_address ----")
    uri = ConfigParse().getItem("uri", "ModifyHomeAddress")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "province": province, "city": city, "district": district, "address": address,
            "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifyHomeAddress json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_home_address ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_home_address ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-CheckPhone")
def check_phone(httpclient, member_id, phone, sms_code, code_token, timestamp=None, logger=None):
    """ Check phone before modify, after getmsgcode, return phone token.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param phone: interface defined parameter phone verified string type.
    :param sms_code: interface defined parameter sms_code after getmsgcode string type.
    :param code_token: interface defined parameter code_token from getmsgcode string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return phone_token successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start check_phone ----")
    uri = ConfigParse().getItem("uri", "CheckPhone")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "phone": phone, "sms_code": sms_code, "code_token": code_token, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("CheckPhone json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end check_phone ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end check_phone ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("User-ModifyPhone")
def modify_phone(httpclient, member_id, phone, sms_code, code_token, phone_token, timestamp=None, logger=None):
    """ Modify phone number, have to getmsgcode and check phone before, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param phone: interface defined parameter phone verified string type.
    :param sms_code: interface defined parameter sms_code after getmsgcode string type.
    :param code_token: interface defined parameter code_token from getmsgcode string type.
    :param phone_token: interface defined paramter phone_token from checkphone string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_phone ----")
    uri = ConfigParse().getItem("uri", "ModifyPhone")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "phone": phone, "sms_code": sms_code, "code_token": code_token,
            "phone_token": phone_token, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifyPhone json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_phone ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_phone ----")
    logger and logger.info("")
    if rsp_content["code"] == 1 and not rsp_content["msg"]:
        return True
    else:
        return False


@allure.step("User-UploadPhoto")
def upload_photo(httpclient, photo_type, member_id, photo, timestamp=None, logger=None):
    """ Upload photo to server, return photo url.
    :param httpclient: http request client.
    :param photo_type: interface defined parameter photo_type int type.
    :param member_id: interface defined parameter member_id return by login string type.
    :param photo: interface defined parameter phone base64 encode type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return photo url dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start upload_photo ----")
    uri = ConfigParse().getItem("uri", "UploadPhoto")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"photo_type": photo_type, "member_id": member_id, "photo": photo, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("UploadPhoto json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end upload_photo ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end upload_photo ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("Account-RelateWX")
def relate_wx(httpclient, member_id, code, timestamp=None, logger=None):
    """ Relate the webchat user to current user, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param code: interface defined parameter code from webchat authentication string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start relate_wx ----")
    uri = ConfigParse().getItem("uri", "RelateWX")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "code": code, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("RelateWX json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end relate_wx ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end relate_wx ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("Account-InfoList")
def account_list(httpclient, member_id, timestamp=None, logger=None):
    """ Get relate accounts list, return dict.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return accounts dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start account_list ----")
    uri = ConfigParse().getItem("uri", "AccountList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"member_id": member_id, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("AccountList json: {}".format(data))
    rsp = httpclient.get(uri=uri, data=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end account_list ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end account_list ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("Account-UnbindWX")
def unbind_wx(httpclient, member_id, auth_id, timestamp=None, logger=None):
    """ Relate the webchat user to current user, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param auth_id: interface defined parameter auth_id of webchat account num string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start unbind_wx ----")
    uri = ConfigParse().getItem("uri", "UnbindWX")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "auth_id": auth_id, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("UnbindWX json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end unbind_wx ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end unbind_wx ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-MyFeature")
def user_myfeature(httpclient, member_id, face_photo, timestamp=None, logger=None):
    """ Identify user by images, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param face_photo: interface defined parameter face_photo from upload photo url string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start user_myfeature ----")
    uri = ConfigParse().getItem("uri", "MyFeature")
    if not timestamp:
        timestamp = get_timestamp()
    params = {"member_id": member_id, "timestamp": get_timestamp()}
    files = {"face_photo": open(get_image_path(face_photo), 'rb')}
    allure.attach("request params", str(params))
    logger and logger.info("UserIdentity json: {}".format(params))
    rsp = httpclient.post(uri, data=params, files=files)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.files", str(files))
    logger and logger.info("request.files: {}".format(files))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end user_myfeature ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end user_myfeature ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("User-Identify")
def user_identity(httpclient, member_id, identity_card_face, identity_card_emblem, timestamp=None, logger=None):
    """ Identify user by images, return True or False.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param identity_card_face: interface defined parameter identity_card_face from upload photo url string type.
    :param identity_card_emblem: interface defined parameter identity_card_emblem from upload photo url string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start user_identity ----")
    uri = ConfigParse().getItem("uri", "UserIdentity")
    if not timestamp:
        timestamp = get_timestamp()
    params = {"member_id": member_id, "timestamp": get_timestamp()}
    files = {"identity_card_face": open(get_image_path(identity_card_face), 'rb'),
             "identity_card_emblem": open(get_image_path(identity_card_emblem), 'rb')}
    allure.attach("request params", str(params))
    logger and logger.info("UserIdentity json: {}".format(params))
    rsp = httpclient.post(uri, data=params, files=files)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.files", str(files))
    logger and logger.info("request.files: {}".format(files))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end user_identity ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end user_identity ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("associates-InfoList")
def get_identity_other_list(httpclient, member_id, page_index, page_size, relationships=None, timestamp=None, orderby=None, logger=None):
    """ Get related peoples of user list.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param page_index: interface defined parameter page_index int type.
    :param page_size: interface defined parameter page_size int type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param orderby: interface defined parameter orderby string type, optional.
    :param relationships: interface defined parameter relationships int(0/1) type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return related peoples dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start get_identity_other_list ----")
    uri = ConfigParse().getItem("uri", "GetIdentityOtherList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"member_id": member_id, "page_index": page_index, "page_size": page_size, "timestamp": timestamp, "orderby": orderby, "relationships": relationships}
    allure.attach("request params", str(data))
    logger and logger.info("GetIdentityOtherList json: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.url", str(rsp.request.url))
    logger and logger.info("request.url: {}".format(rsp.request.url))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end get_identity_other_list ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end get_identity_other_list ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]['data']
    else:
        return {}


@allure.step("associates-Identify")
def identity_other(httpclient, member_id, features_name, other_photo, my_photo, timestamp=None, logger=None):
    """ Identify the related peoples of user.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param features_name: interface defined parameter features_name string type.
    :param other_photo: interface defined parameter other_photo from upload photo url string type.
    :param my_photo: interface defined parameter my_photo from upload photo url string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start identity_other ----")
    uri = ConfigParse().getItem("uri", "IdentityOther")
    if not timestamp:
        timestamp = get_timestamp()
    params = {"member_id": member_id, "features_name": features_name, "timestamp": timestamp}
    files = {"other_photo": open(get_image_path(other_photo), 'rb'),
             "my_photo": open(get_image_path(my_photo), 'rb')}
    allure.attach("request params", str(params))
    logger and logger.info("IdentityOther json: {}".format(params))
    rsp = httpclient.post(uri, data=params, files=files)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.files", str(files))
    logger and logger.info("request.files: {}".format(files))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end identity_other ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end identity_other ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("associates-temp-Identify")
def identity_temp(httpclient, member_id, feature_name, temp_photo, timestamp=None, logger=None):
    """ Identify the related peoples of user.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param features_name: interface defined parameter features_name string type.
    :param temp_photo: interface defined parameter temp_photo from upload photo url string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start identity_temp ----")
    uri = ConfigParse().getItem("uri", "IdentityTemp")
    if not timestamp:
        timestamp = get_timestamp()
    params = {"member_id": member_id, "feature_name": feature_name, "timestamp": timestamp}
    files = {"temp_photo": open(get_image_path(temp_photo), 'rb')}
    allure.attach("request params", str(params))
    logger and logger.info("IdentityOther json: {}".format(params))
    rsp = httpclient.post(uri, data=params, files=files)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.files", str(files))
    logger and logger.info("request.files: {}".format(files))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end identity_temp ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end identity_temp ----")
    logger and logger.info("")
    if rsp_content["Code"] == 1:
        return rsp_content["Result"]
    else:
        return {}


@allure.step("associates-Modify")
def modify_identity_other(httpclient, member_id, features_id, face_picture, community_picture, timestamp=None, logger=None):
    """ Modify related people identity.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param features_id: interface defined parameter features_id string type.
    :param face_picture: interface defined parameter face_picture from upload photo url string type.
    :param community_picture: interface defined parameter community_picture from upload photo url string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start modify_identity_other ----")
    uri = ConfigParse().getItem("uri", "ModifyIdentityOther")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "features_id": features_id, "face_picture": face_picture,
            "community_picture": community_picture, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("ModifyIdentityOther json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end modify_identity_other ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end modify_identity_other ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("associates-Remove")
def remove_identity_other(httpclient, member_id, features_id, timestamp=None, logger=None):
    """ Remove the related people identity.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param features_id: interface defined parameter features_id string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start remove_identity_other ----")
    uri = ConfigParse().getItem("uri", "RemoveIdentityOther")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "features_id": features_id, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("RemoveIdentityOther json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end remove_identity_other ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end remove_identity_other ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("Get-Service-order-list")
def get_myservice_order_list(httpclient, member_id, page_index, page_size, state, orderby=None, search=None, timestamp=None, logger=None):
    """ Get service order list.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param page_index: interface defined parameter page_index int type.
    :param page_size: interface defined parameter page_size int type.
    :param state: interface defined parameter state int type.
    :param orderby: interface defined parameter orderby string type, optional.
    :param search: interface defined parameter search string type, optional.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return services dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start get_myservice_order_list ----")
    uri = ConfigParse().getItem("uri", "GetMyServiceOrderList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"member_id": member_id, "page_index": page_index, "page_size": page_size, "state": state,
            "orderby": orderby, "search": search, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("GetMyServiceOrderList json: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end get_myservice_order_list ----")
        logger and logger.info("")
        return []
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end get_myservice_order_list ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]['data']
    else:
        return []


@allure.step("Suggestion-Feedback")
def feedback(httpclient, member_id, comment, timestamp=None, logger=None):
    """ Post user feedback suggestion of the system.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param comment: interface defined parameter comment string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start feedback ----")
    uri = ConfigParse().getItem("uri", "FeedBack")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "comment": comment, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("FeedBack json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end feedback ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end feedback ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("Get-Application-List")
def get_application_list(httpclient, page_index, page_size, orderby=None, timestamp=None, logger=None):
    """ Get all application list.
    :param httpclient: http request client.
    :param page_index: interface defined parameter page_index int type.
    :param page_size: interface defined parameter page_size int type.
    :param orderby: interface defined parameter orderby string type, optional.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return application dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start get_application_list ----")
    uri = ConfigParse().getItem("uri", "GetApplicationList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"page_index": page_index, "page_size": page_size, "orderby": orderby, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("GetApplicationList json: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end get_application_list ----")
        logger and logger.info("")
        return []
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end get_application_list ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]['data']
    else:
        return []


@allure.step("Get-Recognized-Record-List")
def get_recognized_record_list(httpclient, member_id, page_index, page_size, orderby=None, search=None, timestamp=None, logger=None):
    """ Get recognized record list.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param page_index: interface defined parameter page_index int type.
    :param page_size: interface defined parameter page_size int type.
    :param orderby: interface defined parameter orderby string type, optional.
    :param search: interface defined paramter search string type, optional.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return recognized record dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start get_recognized_record_list ----")
    uri = ConfigParse().getItem("uri", "GetRecognizedRecordList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"member_id": member_id, "page_index": page_index, "page_size": page_size,
            "orderby": orderby, "search": search, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("GetRecognizedRecordList json: {}".format(data))
    rsp = httpclient.get(uri=uri, data=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end get_recognized_record_list ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end get_recognized_record_list ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("App-CheckVersion")
def check_version(httpclient, package_type, package_version, timestamp=None, logger=None):
    """ Get recognized record list.
    :param httpclient: http request client.
    :param package_type: interface defined parameter package_type int type.
    :param package_version: interface defined parameter package_version string type.
    :param timestamp: interface defined parameter timestamp int type..
    :param logger: logger instance for logging, optional.
    :rtype: return recognized record dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start check_version ----")
    uri = ConfigParse().getItem("uri", "GetRecognizedRecordList")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"package_type": package_type, "package_version": package_version, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("GetRecognizedRecordList json: {}".format(data))
    rsp = httpclient.get(uri=uri, data=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end check_version ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end check_version ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("H5-Get-Authentication")
def h5_get_business_token(httpclient, member_id, timestamp=None, logger=None):
    """ Business system H5 get the user authentication info.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return authentication info dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start h5_get_business_token ----")
    uri = ConfigParse().getItem("uri", "H5GetAuthentication")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("H5GetAuthentication json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end h5_get_business_token ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end h5_get_business_token ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("Inner-Auth")
def inner_auth(httpclient, member_id, timestamp=None, logger=None):
    """ Business system H5 get the user authentication info.
    :param httpclient: http request client.
    :param member_id: interface defined parameter member_id return by login string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return authentication info dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start inner_auth ----")
    uri = ConfigParse().getItem("uri", "INAuth")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"member_id": member_id, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("INAuth json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end inner_auth ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end inner_auth ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("Inner-Create-Service-Order")
def inner_create_service_order(httpclient, system_id, business_order_id, member_id, feature_id, device_ids,
                            verify_condition_type, begin_time, end_time, in_count, spu_id, service_unit,
                            service_address, timestamp=None, logger=None):
    """ Business system submit service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param business_order_id: interface defined parameter business_order_id string type.
    :param member_id: interface defined parameter member_id long type.
    :param feature_id: interface defined parameter feature_id long type.
    :param devices_ids: interface defined parameter devices_ids string array type.
    :param verify_condition_type: interface defined parameter verify_condition_type int type.
    :param begin_time: interface defined parameter begin_time long type, optional.
    :param end_time: interface defined parameter end_time long type, optional.
    :param in_count: interface defined parameter in_count int type, optional.
    :param spu_id: interface defined parameter spu_id string type.
    :param service_unit: interface defined parameter service_unit string type.
    :param service_address: interface defined parameter service_address string type.
    :param timestamp: interface defined parameter Timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return service order dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start inner_create_service_order ----")
    uri = ConfigParse().getItem("uri", "INCreate")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "business_order_id": business_order_id, "member_id": member_id,
            "feature_id": feature_id, "device_ids": device_ids, "verify_condition_type": verify_condition_type,
            "begin_time": begin_time, "end_time": end_time, "in_count": in_count, "spu_id": spu_id,
            "service_unit": service_unit, "service_address": service_address, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("INCreate json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end inner_create_service_order ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end inner_create_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("Inner-Close-Service-Order")
def inner_close_service_order(httpclient, system_id, service_order_id, close_code, timestamp=None, logger=None):
    """ Business system cancel service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param service_order_id: interface defined parameter service_order_id string type.
    :param close_code: interface defined parameter close_code int type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start inner_close_service_order ----")
    uri = ConfigParse().getItem("uri", "INClose")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "service_order_id": service_order_id, "close_code": close_code, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("INClose json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end inner_close_service_order ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end inner_close_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("BS-Get-UserInfo")
def bs_get_user_info(httpclient, system_id, member_id, business_token, timestamp=None, logger=None):
    """ Business system get user info from server.
    :param httpclient: http request client.
    :param system_id: the business system id long type.
    :param member_id: interface defined parameter member_id return by login long type.
    :param business_token: interface defined parameter business_token from business system string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return user info dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_get_user_info ----")
    uri = ConfigParse().getItem("uri", "BSGetUserInfo")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"system_id": system_id, "member_id": member_id, "business_token": business_token, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("BSGetUserInfo json: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_get_user_info ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_get_user_info ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("H5-Create-Service-Order")
def h5_create_service_order(httpclient, system_id, business_order_id, member_id, system_code, features_id, device_ids,
                            verify_condition_type, begin_time, end_time, in_count, service_unit, service_address, timestamp=None, logger=None):
    """ Business system submit service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param business_order_id: interface defined parameter business_order_id string type.
    :param member_id: interface defined parameter member_id long type.
    :param system_code: interface defined parameter system_code string type.
    :param features_id: interface defined parameter features_id long type.
    :param devices_ids: interface defined parameter devices_ids string array type.
    :param verify_condition_type: interface defined parameter verify_condition_type int type.
    :param begin_time: interface defined parameter begin_time long type, optional.
    :param end_time: interface defined parameter end_time long type, optional.
    :param in_count: interface defined parameter in_count int type, optional.
    :param service_unit: interface defined parameter service_unit string type.
    :param service_address: interface defined parameter service_address string type.
    :param timestamp: interface defined parameter Timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return service order dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_create_service_order ----")
    uri = ConfigParse().getItem("uri", "H5CreateServiceOrder")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "business_order_id": business_order_id, "member_id": member_id, "system_code": system_code,
            "features_id": features_id, "device_ids": device_ids, "verify_condition_type": verify_condition_type,
            "begin_time": begin_time, "end_time": end_time, "in_count": in_count, "service_unit": service_unit,
            "service_address": service_address, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("BSCreateServiceOrder json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_create_service_order ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_create_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("BS-Create-Service-Order")
def bs_create_service_order(httpclient, system_id, business_order_id, system_code, features_id, device_ids,
                            verify_condition_type, begin_time, end_time, in_count, service_unit, service_address, timestamp=None, logger=None):
    """ Business system submit service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param business_order_id: interface defined parameter business_order_id string type.
    :param system_code: interface defined parameter system_code string type.
    :param features_id: interface defined parameter features_id long type.
    :param devices_ids: interface defined parameter devices_ids string array type.
    :param verify_condition_type: interface defined parameter verify_condition_type int type.
    :param begin_time: interface defined parameter begin_time long type, optional.
    :param end_time: interface defined parameter end_time long type, optional.
    :param in_count: interface defined parameter in_count int type, optional.
    :param service_unit: interface defined parameter service_unit string type.
    :param service_address: interface defined parameter service_address string type.
    :param timestamp: interface defined parameter Timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return service order dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_create_service_order ----")
    uri = ConfigParse().getItem("uri", "BSCreateServiceOrder")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "business_order_id": business_order_id, "system_code": system_code,
            "features_id": features_id, "device_ids": device_ids, "verify_condition_type": verify_condition_type,
            "begin_time": begin_time, "end_time": end_time, "in_count": in_count, "service_unit": service_unit,
            "service_address": service_address, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("BSCreateServiceOrder json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_create_service_order ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_create_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("BS-Update-Service-Order")
def bs_update_service_order(httpclient, system_id, service_order_id, system_code, features_id, devices_id,
                            verify_condition_type, begin_time, end_time, in_count, service_unit, service_address, timestamp=None, logger=None):
    """ Business system update service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param service_order_id: interface defined parameter service_order_id string type.
    :param system_code: interface defined parameter system_code string type.
    :param features_id: interface defined parameter features_id long type.
    :param devices_id: interface defined parameter devices_id long array type.
    :param verify_condition_type: interface defined parameter verify_condition_type int type.
    :param begin_time: interface defined parameter begin_time long type, optional.
    :param end_time: interface defined parameter end_time long type, optional.
    :param in_count: interface defined parameter in_count int type, optional.
    :param service_unit: interface defined parameter service_unit string type.
    :param service_address: interface defined parameter service_address string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_update_service_order ----")
    uri = ConfigParse().getItem("uri", "BSUpdateServiceOrder")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "service_order_id": service_order_id, "system_code": system_code, "features_id": features_id,
            "device_id": devices_id, "verify_condition_type": verify_condition_type, "begin_time": begin_time,
            "end_time": end_time, "in_count": in_count, "service_unit": service_unit, "service_address": service_address, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("BSUpdateServiceOrder json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_update_service_order ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_update_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False


@allure.step("BS-Close-Service-Order")
def bs_close_service_order(httpclient, system_id, service_order_id, system_code, close_code, timestamp=None, logger=None):
    """ Business system cancel service order to server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param service_order_id: interface defined parameter service_order_id string type.
    :param system_code: interface defined parameter system_code string type.
    :param close_code: interface defined parameter close_code int type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_close_service_order ----")
    uri = ConfigParse().getItem("uri", "BSCancelServiceOrder")
    if not timestamp:
        timestamp = get_timestamp()
    json = {"system_id": system_id, "service_order_id": service_order_id, "system_code": system_code, "close_code": close_code, "timestamp": timestamp}
    allure.attach("request params", str(json))
    logger and logger.info("BSCancelServiceOrder json: {}".format(json))
    rsp = httpclient.post(uri=uri, json=json)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_close_service_order ----")
        logger and logger.info("")
        return False
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_close_service_order ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return True
    else:
        return False

@allure.step("BS-Get-Service-Order-Status")
def bs_get_service_order_status(httpclient, system_id, service_order_id, system_code, timestamp=None, logger=None):
    """ Business system service order status from server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param service_order_id: interface defined parameter service_order_id string type.
    :param system_code: interface defined parameter system_code string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return order info dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_get_service_order_status ----")
    uri = ConfigParse().getItem("uri", "BSServiceOrderStatus")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"system_id": system_id, "service_order_id": service_order_id, "system_code": system_code, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("BSServiceOrderStatus data: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_get_service_order_status ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_get_service_order_status ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("BS-Get-Service-Order-Records")
def bs_get_service_order_records(httpclient, system_id, service_order_id, system_code, page_index, page_size, timestamp=None, logger=None):
    """ Business system service order status from server.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param service_order_id: interface defined parameter service_order_id string type.
    :param system_code: interface defined parameter system_code string type.
    :param page_index: interface defined parameter page_index int type.
    :param page_size: interface defined parameter page_size int type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return record info dict successfully, {} failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_get_service_order_records ----")
    uri = ConfigParse().getItem("uri", "BSServiceOrderRecord")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"system_id": system_id, "service_order_id": service_order_id, "system_code": system_code, "page_index": page_index,
            "page_size": page_size, "timestamp": timestamp}
    allure.attach("request params", str(data))
    logger and logger.info("BSServiceOrderRecord data: {}".format(data))
    rsp = httpclient.get(uri=uri, params=data)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_get_service_order_records ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_get_service_order_records ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content["result"]
    else:
        return {}


@allure.step("BS-Service-Order-GenFeatureId")
def bs_service_order_gen_featureid(httpclient, system_id, system_code, name, photo, member_id=None, timestamp=None, logger=None):
    """ Business system generate feature id by upload picture.
    :param httpclient: http request client.
    :param system_id: interface defined parameter system_id long type.
    :param member_id: interface defined parameter member_id long type.
    :param system_code: interface defined parameter system_code string type.
    :param name: interface defined parameter name string type.
    :param photo: interface defined parameter photo string type.
    :param timestamp: interface defined parameter timestamp int type, optional.
    :param logger: logger instance for logging, optional.
    :rtype: return True successfully, False failed.
    """
    logger and logger.info("")
    logger and logger.info("---- start bs_service_order_gen_featureid ----")
    uri = ConfigParse().getItem("uri", "BSGenFeatureId")
    if not timestamp:
        timestamp = get_timestamp()
    data = {"system_id": system_id, "member_id": member_id, "system_code": system_code, "name": name, "timestamp": timestamp}
    files = {"photo": open(get_image_path(photo), 'rb')}
    allure.attach("request params", str(data))
    logger and logger.info("BSCancelServiceOrder json: {}".format(data))
    rsp = httpclient.post(uri=uri, data=data, files=files)
    allure.attach("request.headers", str(rsp.request.headers))
    logger and logger.info("request.headers: {}".format(rsp.request.headers))
    allure.attach("request.body", str(rsp.request.body))
    logger and logger.info("request.body: {}".format(rsp.request.body))
    status_code = rsp.status_code
    allure.attach("status_code", str(status_code))
    logger and logger.info("status_code: {}".format(status_code))
    if status_code != 200:
        allure.attach("response content", str(rsp.text))
        logger and logger.info("response content: {}".format(rsp.text))
        logger and logger.info("---- end bs_close_service_order ----")
        logger and logger.info("")
        return {}
    rsp_content = rsp.json()
    allure.attach("response content", str(rsp_content))
    logger and logger.info("response content: {}".format(rsp_content))
    logger and logger.info("---- end bs_service_order_gen_featureid ----")
    logger and logger.info("")
    if rsp_content["code"] == 1:
        return rsp_content['result']
    else:
        return {}


@allure.step("IOT-Subscribe-Msg")
def subscribe_msg(ProductKey, DeviceName, DeviceSecret, topic, qos, queue):
    """ Tool function for mqtt subscribe message.
    :param ProductKey: ali iot platform productkey string type.
    :param DeviceName: ali iot platform devicename string type.
    :param DeviceSecret: ali iot platform devicesecret string type.
    :param topic: subscribe topic string type.
    :param qos: subscribe topic's qos int type.
    :param queue: store subscribe message queue.
    :rtype None.
    """
    params = AliParam(ProductKey=ProductKey, DeviceName=DeviceName, DeviceSecret=DeviceSecret)
    clientid, username, password, hostname = params.get_param()
    authconfig = {'username': username, 'password': password}
    msg = subscribe_simple(topic, qos, 1, client_id=clientid, hostname=hostname, port=1883,
                           auth=authconfig)
    queue.put(msg)


@allure.step("IOT-Subscribe-Message")
def iot_subscribe_message(ProductKey, DeviceName, DeviceSecret, topic, qos, timeout=60):
    """ Subscribe iot message.
    :param ProductKey: ali iot platform productkey string type.
    :param DeviceName: ali iot platform devicename string type.
    :param DeviceSecret: ali iot platform devicesecret string type.
    :param topic: subscribe topic string type.
    :param qos: subscribe topic's qos int type.
    :param timeout: subscribe message threading timeout int type, default 60s.
    :rtype return dict of payload message, or {} failed.
    """
    queue = Queue()
    t1 = threading.Thread(target=subscribe_msg, args=(ProductKey, DeviceName, DeviceSecret, topic, qos, queue))
    t1.start()
    start_time = int(time.time())
    sleep(5)
    end_time = int(time.time())
    during = end_time - start_time
    while t1.is_alive() and during < timeout:
        sleep(5)
        end_time = int(time.time())
        during = end_time - start_time
    if t1.is_alive():
        stop_thread(t1)
        return {}
    if queue.empty():
        return {}
    msg = queue.get()
    return msg.payload


@allure.step("IOT-Publish-ServiceOrderReport")
def iot_publish_ServiceOrderReport(mqttclient, productkey, devicename, service_order_id, device_id, in_out=1, qos=1, exrea="", logger=None):
    """ Publish iot message.
    :param mqttclient: mqtt client.
    :param productkey: ali iot platform productkey string type.
    :param devicename: ali iot platform devicename string type.
    :param service_order_id: publish payload service_order_id.
    :param device_id: publish payload device_id.
    :param in_out: publish payload in_out.
    :param exrea: publish payload exrea.
    :param qos: publish topic's qos int type.
    :rtype return None.
    """
    logger and logger.info("")
    logger and logger.info("---- start iot_publish_ServiceOrderReport ----")
    tname = ConfigParse().getItem("iot", "ServiceOrderReport")
    topic = "/{0}/{1}/{2}".format(productkey, devicename, tname)
    payload = {
        "action_id": "100",
        "data": {
            "service_order_id": str(service_order_id),
            "device_id": str(device_id),
            "in_out": str(in_out),
            "exrea": exrea,
        },
        "timestamp": str(get_timestamp())
    }
    logger and logger.info("topic: {0}".format(topic))
    logger and logger.info("in payload: {0}".format(payload))
    logger and logger.info("qos: {0}".format(qos))
    mqttclient.publish(topic, str(payload), qos)
    logger and logger.info("---- end iot_publish_ServiceOrderReport ----")
    logger and logger.info("")


@allure.step("IOT-Publish-SyncTime")
def iot_publish_SyncTime(mqttclient, productkey, devicename, qos=1, data="", timeout=60, logger=None):
    """ Publish iot message.
    :param mqttclient: mqtt client.
    :param productkey: ali iot platform productkey string type.
    :param devicename: ali iot platform devicename string type.
    :param data: publish payload exrea.
    :param qos: publish topic's qos int type.
    :param timeout: subscribe mqtt message timeout.
    :param logger: logger.
    :rtype return None.
    """
    logger and logger.info("")
    logger and logger.info("---- start iot_publish_SyncTime ----")
    upstr = ConfigParse().getItem("iot", "TimeUp")
    downstr = ConfigParse().getItem("iot", "TimeDown")
    req_topic = "/{0}/{1}/{2}".format(productkey, devicename, upstr)
    rsp_topic = "/{0}/{1}/{2}".format(productkey, devicename, downstr)
    req_payload = {
        "action_id": "104",
        "data": data,
        "timestamp": str(get_timestamp())
    }
    logger and logger.info("request topic: {0}".format(req_topic))
    logger and logger.info("request payload: {0}".format(req_payload))
    logger and logger.info("response topic: {0}".format(rsp_topic))
    mqttclient.subscribe(rsp_topic, qos)
    mqttclient.loopstart()
    mqttclient.publish(req_topic, str(req_payload), qos)
    start_time = int(time.time())
    end_time = int(time.time())
    during = end_time - start_time
    while not mqttclient.rcv_msg and during < timeout:
        sleep(5)
        end_time = int(time.time())
        during = end_time - start_time
    mqttclient.loopstop()
    mqttclient.unsubscribe(rsp_topic)
    if mqttclient.rcv_msg:
        msg = mqttclient.rcv_msg.pop()
        payload = json.loads(msg.payload, encoding='utf-8')
        logger and logger.info("message payload: {}".format(payload))
        logger and logger.info("---- end iot_publish_SyncTime ----")
        logger and logger.info("")
        return payload
    else:
        logger and logger.info("---- end iot_publish_SyncTime ----")
        logger and logger.info("")
        return {}


@allure.step("Register Function")
def make_register(httpclient, client_type, client_version, device_token, imei, code_type, phone, sms_code, timestamp=None, logger=None):
    """ Register function, return True or False.
        :param httpclient: http request client.
        :param client_type: interface defined paramter client_type int type.
        :param client_version: interface defined parameter client_version string type.
        :param device_token: interface defined parameter device_token string type.
        :param imei: interface defined parameter client phone imei string type.
        :param code_type: interface defined paramter code_type int type.
        :param phone: interface defined parameter phone string type.
        :param timestamp: interface defined parameter timestamp int type, optional.
        :param logger: logger instance for logging, optional.
        :rtype: True successful, False failed.
        """
    with allure.step("GetMsgCode"):
        code_token = get_msg_code(httpclient, code_type, phone, timestamp, logger)
        allure.attach("GetMsgCode: ", str(code_token))
        logger.info("GetMsgCode result: " + str(code_token))
        if code_token == "":
            return {}

    with allure.step("Register"):
        register_result = register(httpclient, client_type, client_version, device_token, imei, phone, code_token, sms_code, get_timestamp(), logger=logger)
        allure.attach("Register result: ", str(register_result))
        logger.info("Register result: {0}".format(register_result))
        if not register_result:
            return {}
    return register_result


@allure.step("Login Function")
def make_login(httpclient, code_type, client_type, client_version, device_token, imei, phone, sms_code, timestamp=None, logger=None):
    """ APP login interface, return login user info dict.
        :param httpclient: http request client.
        :param client_type: interface defined paramter client_type int type.
        :param client_version: interface defined parameter client_version string type.
        :param device_token: interface defined parameter device_token string type.
        :param imei: interface defined parameter client phone imei string type.
        :param phone: interface defined parameter register phone number string type.
        :param sms_code: run interface GetMsgCode get from phone sms code string type.
        :param timestamp: interface defined parameter timestamp int type, optional.
        :param logger: logger instance for logging, optional.
        :rtype: result dict login successfully, {} login failed.
        """
    code_token = get_msg_code(httpclient, code_type, phone, timestamp, logger)
    if not code_token:
        return {}
    result = app_login(httpclient, client_type, client_version, device_token, imei, phone, sms_code, code_token, timestamp, logger)
    return result
