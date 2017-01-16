# -*- coding:utf-8 -*-

import requests
import threading
import datetime
from bs4 import BeautifulSoup
import re

class Zhilian(threading.Thread):
    def __init__(self, city, keyword):
        threading.Thread.__init__(self)
        self.city = city
        self.keyword = keyword
        self.headers = {
            'Host': 'sou.zhaopin.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        self.time = datetime.datetime.now()
        if self.time.month < 10:
            self.month = "0" + str(self.time.month)
        else:
            self.month = str(self.time.month)
        if self.time.day < 10:
            self.day = "0" + str(self.time.day)
        else:
            self.day = str(self.time.day)
        self.today = self.month + "-" + self.day

        self.session = requests.Session()

    def run(self):
        self.url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl='+self.city+'&kw='+self.keyword+'&sm=0&p=1'
        html = self.session.get(self.url, headers=self.headers)
        bsobj = BeautifulSoup(html.text, 'html.parser')
        newlists = bsobj.findAll('table', {'class', 'newlist'})
        for i in range(1, len(newlists)):
            link = newlists[i].find('tr').find('a')['href']
            position, salary, experience, education, Description_and_requirements, area, companyName, companyNature, companyPersonnel, companyInfo = self.get_infos(link)

    def get_infos(self, url):
        try:
            self.headers['Host'] = 'job.zhaopin.com'

            html = self.session.get(url, headers=self.headers)
            bs = BeautifulSoup(html.text, 'html.parser')
            # 职位
            position = bs.find('div', {'class', 'inner-left fl'}).find('h1').get_text()

            lis = bs.find('ul', {'class', 'terminal-ul clearfix'}).find('li')
            # 薪资
            salary = lis[0].find('strong').get_text()
            lname = lis[1].find('strong').get_text()
            # 要求经验
            experience = lis[4].find('strong').get_text()
            # 要求学历
            education = lis[5].find('strong').get_text()

            infos = bs.findAll('div', {'class', 'tab-inner-cont'})
            # 职位描述和任职要求
            Description_and_requirements = re.findall(r'(.*?)\n', infos[0].get_text())[2]

            a = infos[0].find('h2').get_text().replace('\n', '').replace(' ', '')
            # 工作地点
            area = lname + '-' + a

            companyInfos = bs.find('div', {'class', 'company-box'}).findAll('li')
            # 公司名字
            companyName = bs.find('div', {'class', 'inner-left fl'}).find('h2').get_text()
            # 公司规模
            companyPersonnel = companyInfos[0].find('strong').get_text()
            # 公司性质
            companyNature = companyInfos[1].find('strong').get_text()
            # 公司介绍
            companyInfo = infos[1].findAll('p')[0].get_text()

            return position, salary, experience, education, Description_and_requirements, area, companyName, companyNature, companyPersonnel, companyInfo

        except Exception as e:
            print e.message

city = '上海'
keyword = 'python'
t = Zhilian(city, keyword)
t.start()


