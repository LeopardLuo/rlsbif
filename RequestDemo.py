#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import time

with requests.session() as s:
    s.headers.update({'PhoneSeri': 'Android123456'})
    r = s.get("http://192.168.0.105:9088/api/Theme/GetTheme")
    print(s.headers)
    print(r.text)
    
    
    """
    phonenum = "15828391115"
    print("\n获取验证码：")
    data = {"PhoneNumber": phonenum}
    r = s.post("http://192.168.0.105:9088/api/Reg/RegCode", json=data)
    print(s.headers)
    print(r.text)
    
    print("\n确认验证码：")
    data_confirm = {"PhoneNumber": phonenum, "VerifyCode": "1234", "Pwd": "123abc"}
    r = s.post("http://192.168.0.105:9088/api/Reg/VerifyRegCode", json=data_confirm)
    rsp = r.json()
    print(rsp)
    memberid = rsp["Data"]["MemberId"]
    
    print("\n保存注册：")
    save_reg = {"MemberId":memberid, "TempleID": '语音山房', "Name": 'YYSF', "IDCard": "440181198011024220", 
                "Sex": '0', "Birthday": "1980-11-2", "PresentAddress": "番禺南村"}
    filename = {"Icon": open('img/Kaola.jpg', 'rb')}
    r1 = s.post("http://192.168.0.105:9088/Api/Reg/SaveRegister", data=save_reg, files=filename)
    print(save_reg)
    print(s.headers)
    print(r1.status_code)
    rsp = r1.json()
    print(rsp)
    token = 'Bearer ' + rsp['Data']['Token']
    print(token)
    
    s.headers.update({"Authorization": token})
    print("\n修改密码-获取验证:")
    data = {"PhoneNumber": phonenum}
    r = s.post("http://192.168.0.105:9088/api/Pwd/GetCode", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n修改密码-确认验证码:")
    data = {"PhoneNumber": phonenum, "VerifyCode": "1234", "Pwd": "123456abc"}
    r = s.post("http://192.168.0.105:9088/api/Pwd/VerifyCode", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n变更手机-密码确认：")
    data = {"PhoneNumber": phonenum, "Pwd": "b1a96e54a5e9527abd2bc8f298c33fce69c55ceeea404611f08e1b3f2d22357b"}
    r = s.post("http://192.168.0.105:9088/api/Member/AlterConfirmPwd", json=data)
    print(r.status_code)
    print(r.json())
    
    newphone = '15828392111'
    print("\n变更手机-获取验证码:")
    data = {"PhoneNumber": newphone}
    r = s.post("http://192.168.0.105:9088/api/Member/AlterGetCode", json=data)
    print(r.status_code)
    rsp = r.json()
    print(rsp)
    
    print("\n变更手机-校验验证码:")
    data = {"MemberID": memberid, "PhoneNumber": phonenum, "NewPhoneNumber": newphone, "VerifyCode": "1234"}
    r = s.post("http://192.168.0.105:9088/api/Member/AlterConfirmCode", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n退出登录：")
    data = {"MemberId":memberid}
    r = s.post("http://192.168.0.105:9088/Api/Member/Logout", json=data)
    print(r.status_code)
    print(r.json())
    """
    
    newphone = '15828392111'
    print("\n登录：")
    data = {"PhoneNumber": newphone, "Pwd": "b1a96e54a5e9527abd2bc8f298c33fce69c55ceeea404611f08e1b3f2d22357b"}
    r = s.post("http://192.168.0.105:9088/Api/Member/Login", json=data)
    rsp = r.json()
    print(r.status_code)
    print(rsp)
    memberid = rsp["Data"]["MemberID"]
    token = 'Bearer ' + rsp['Data']['Token']
    s.headers.update({"Authorization": token})
    
    print("\n修改个人信息：")
    data = {"MemberId":(None, memberid), "TempleID": (None, '语音山房'), "Name": (None, 'YYSF'), "PresentAddress": (None, "番禺南村北大街4号")}
    r = s.post("http://192.168.0.105:9088/Api/Member/SaveMember", files=data)
    print(r.status_code)
    print(r.request.headers)
    print(r.request.body.decode())
    print(r.json())
    
    print("\n获取版本信息：")
    data = {"ClientVersion": "0.0.0.1", "DeviceType": "0"}
    r = s.post("http://192.168.0.105:9088/api/upgrade/LastVersion", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n获取引导页信息：")
    r = s.get("http://192.168.0.105:9088/api/Theme/GetTheme")
    print(r.status_code)
    print(r.json())
    
    print("\n意见提交：")
    data = {"MemberId":memberid, "Contact": newphone, "Content": "This is my idea."}
    filename = {"File1": open("img/Kaola.jpg", 'rb')}
    r = s.post("http://192.168.0.105:9088/api/Suggestion/SaveSuggestion", data=data, files=filename)
    print(r.status_code)
    print(r.json())
    
    print("\n获取祖庙信息：")
    r = s.get("http://192.168.0.105:9088/api/Temple/GetTemple")
    print(r.status_code)
    print(r.json())
    
    print("\n绑定-新增：")
    data = {"MemberId":memberid, "MacAddress": "00:00:01:00:00:01", "DeviceSerial": "GDH123456789", "TotalKT": '100', "TotalSJ": '100'}
    r = s.post("http://192.168.0.105:9088/api/Device/SaveBinding", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n绑定-获取列表：")
    data = {"MemberId":memberid}
    r = s.post("http://192.168.0.105:9088/api/Device/GetList", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n绑定-验证设备绑定：")
    data = {"MemberId":memberid, "DeviceSerial": "GDH123456789"}
    r = s.post("http://192.168.0.105:9088/api/Device/ValidateConnect", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n录入个人历史总数：")
    data = {"MemberId":memberid, "CountSJ": "333", "CountKT": "444"}
    r = s.post("http://192.168.0.105:9088/api/Data/SaveHistoryGdz", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n同步：")
    data = {
        "GdzDataInput":[{
            "MemberId":memberid, 
            "DeviceSerial": "GDH123456789",
            "TimeStamp": str(round(time.time())), 
            "Alt": "10.5", 
            "Lon": "113.1234", 
            "Lat": "23.2342", 
            "TimeStampType": "1",
            "GdzType": "1", 
            "Count": "320", 
            "Total": "100000"
            }]
        }
    r = s.post("http://192.168.0.105:9088/api/Data/SaveGdz", json=data)
    print(r.status_code)
    print(r.request.body.decode())
    print(r.json())
    
    print("\n排行榜：")
    data = {"MemberId":memberid, "GdzType": "1", "PageIndex": "1"}
    r = s.post("http://192.168.0.105:9088/api/Data/GetGdzRank", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n个人统计：")
    data = {"MemberId":memberid, "GdzType": "1", "CountType": "1", "RankDate": "2018-9-6", "TimeZone": "8"}
    r = s.post("http://192.168.0.105:9088/api/Data/CountGdz", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n绑定-解除：")
    data = {"MemberId":memberid, "DeviceSerial": "GDH123456789"}
    r = s.post("http://192.168.0.105:9088/api/Device/RemoveBinding", json=data)
    print(r.status_code)
    print(r.json())
    
    print("\n退出登录：")
    data = {"MemberId":memberid}
    r = s.post("http://192.168.0.105:9088/Api/Member/Logout", json=data)
    print(r.request.headers)
    print(r.status_code)
    print(r.json())
    