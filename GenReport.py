#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
import time
import re

cmd = 'allure generate report/ -o report/' + str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '/'
print(cmd)
r = os.popen(cmd)
output = r.read()
if re.match(r'Report successfully', output):
    print("Report generate successfully!")
else:
    print("Report generate failed!")
print("------ Finished ------")
