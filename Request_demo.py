#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import requests.utils

url = 'https://api.github.com/events'
headers = {'user-agent': 'my-broser/0.0.1'}
r = requests.get(url, headers=headers)
print(r.status_code)
print(r.raw)
print(r.content)
print(r.json())
print()

url = 'http://httpbin.org/get'
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
r = requests.get(url, params=payload)
print(r.url)
print()

payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post("http://httpbin.org/post", data=payload)
print(r.text)
print()

data = {'some': 'data'}
r = requests.post('https://api.github.com/some/endpoint', json=data)
print(r.status_code)
print()

url = 'http://httpbin.org/post'
files = {'file': (open('img/16px.png', 'rb'), 'multipart/form-data')}
r = requests.post(url, files=files)
print(r.text)

print()
s = requests.session()
r = s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
print(r.text)
r = s.get('http://httpbin.org/cookies')
print(r.text)

print()
s = requests.session()
s.auth = ('user', 'passwd')
s.headers.update({'x-text': 'true'})
r = s.get('http://httpbin.org/headers', headers={'x-text2': 'true'})
print(r.text)

print()
s = requests.session()
r = s.get('http://httpbin.org/cookies', cookies={'from-my': 'browser'})
print(r.text)
cookiejar = requests.utils.cookiejar_from_dict({'cookie': 'value'})
s.cookies = cookiejar
r = s.get('http://httpbin.org/cookies')
print(r.text)

print()
with requests.session() as s:
    r = s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
    print(r.text)

print()
with requests.session() as s:
    data = {'key1': 'value1', 'key2': 'value2'}
    files = [('image1',('16px1.png', open('img/16px.png', 'rb'), 'image/png')),
             ('image2', ('16px2.png', open('img/16px.png', 'rb'), 'image/png'))]
    r = s.post('http://httpbin.org/post', data=data, files=files)
    print(r.text)

print("****** GET verb *****")
with requests.session() as s:
    r = s.get('https://api.github.com/repos/requests/requests/git/commits/a050faf084662f3a352dd1a941f2c7c9f886d4ad')
    if r.status_code == requests.codes.ok:
        print(r.headers['content-type'])
        rsp_data = r.json()
        print(rsp_data.keys())
        print(rsp_data['url'])
        print(rsp_data['message'])

print("\n****** options verb ********")
with requests.session() as s:
    r = s.options('https://www.baidu.com', timeout=(5, 5))
    print(r.text)