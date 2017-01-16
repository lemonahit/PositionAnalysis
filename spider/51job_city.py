# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import csv

import re

headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
    }

session = requests.Session()
url = 'http://js.51jobcdn.com/in/js/2016/layer/area_array_c.js'
html = session.get(url, headers=headers)

filepath = '/Users/edz/Documents/project/PositionAnalysis/citys.csv'
f = open(filepath, 'a')
writer = csv.writer(f)
writer.writerow(['CityName', 'CityId'])
citys = re.findall(r'\n(.*?),', html.text)
cs = []
for i in range(len(citys)):
    city = (citys[i][10:-1], citys[i][1:7])
    cs.append(city)
writer.writerows(cs)
f.close()
