# -*- coding:utf-8 -*-

import requests
import urllib2
import json
from bs4 import BeautifulSoup as bf
import re
import time
import pymysql


# 头部信息
def handler(url):
    session = requests.Session()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    headers = {
        'Host': 'www.lagou.com',
        'User-Agent': user_agent,
        'Upgrade-Insecure-Requests': '1',
    }
    html = session.get(url, headers=headers, verify=False, timeout=6)
    return html


# 获取某职位所有的页数
def searchPage(position):
    url = 'https://www.lagou.com/jobs/list_' + position + '?labelWords=&fromSearch=true&suginput='
    html = handler(url)
    bsobj = bf(html.text, 'html.parser')
    pages = bsobj.find('span', {'class': 'span totalNum'}).get_text()
    return pages

# 获取职位的链接
def getLinks(position, city):
    pages = searchPage(position)
    links = []
    for i in range(0, int(pages)):
        url = 'http://www.lagou.com/jobs/positionAjax.json?city=' + city + '&first=true&kd=' + position + '&pn=' + str(i + 1)
        print url
        req = urllib2.Request(url)
        # html = urllib2.urlopen(req).read()
        try:
            html = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print e.code
            print e.reason
            print e.geturl()
            print e.read()
        rdict = json.loads(html)
        rcontent = rdict["content"]
        rresults = rcontent["positionResult"]["result"]
        num = rcontent["pageSize"]
        for i in range(0, num):
            positionId = rresults[i]["positionId"]
            link = "http://lagou.com/jobs/" + str(positionId) + ".html"
            links.append(link)
    return links

# 获取职位信息
def get_information(position, city):
    conn = pymysql.connect(host='localhost', user='root', passwd=None, port=3306, use_unicode=True, charset='utf8mb4')
    cur = conn.cursor()
    cur.execute('create database if not EXISTS PositionAnalysis')
    cur.execute('use PositionAnalysis')
    cur.execute('drop table lagou_position_info')
    cur.execute('create table lagou_position_info '
                '(PositionId int PRIMARY KEY ,'
                'Position VARCHAR(100), '
                'Salary VARCHAR(100),'
                'Publish_time VARCHAR(100),'
                'City VARCHAR(100),'
                'District VARCHAR(100),'
                'BizArea VARCHAR(100),'
                'Address VARCHAR(100),'
                'CompanyId int,'
                'Company VARCHAR(100),'
                'CompanyLink VARCHAR(100),'
                'Description TEXT)')

    links = getLinks(position, city)
    for i in range(len(links)):
        time.sleep(3)
        html = handler(links[i])
        # print('正在解析第%d个职位...' % i)
        bsobj = bf(html.text, 'html.parser')

        # 职位ID
        positionId = re.findall('\d+', links[i])[0]
        positionId = int(positionId)

        # 职位名称
        position = bsobj.find('span', {'class': 'name'}).get_text()

        # 薪资
        salary = bsobj.find('span', {'class': 'salary'}).get_text()

        #发布时间
        publish_time = bsobj.find('p', {'class': 'publish_time'}).get_text()

        # 公司地址
        city = bsobj.find('div', {'class': 'work_addr'}).findAll(re.compile('a'))[0].get_text()
        if city == '':
            city = None
        try:
            district = re.findall(r'city=.*&district=.*#filterBox\">(.*?)<\/a>', html.text)[0]
        except:
            district = None
        try:
            bizArea = re.findall(r'bizArea=.*\#filterBox\">(.*?)<\/a>', html.text)[0]
        except:
            bizArea = None
        if district == None:
            address = re.findall('a>\s+(.*?)\s+<a rel="nofollow"', html.text)[1].replace('-', '').replace(' ', '')
        elif bizArea == None:
            address = re.findall('a>\s+(.*?)\s+<a rel="nofollow"', html.text)[2].replace('-', '').replace(' ', '')
        else:
            address = re.findall('a>\s+(.*?)\s+<a rel="nofollow"', html.text)[3].replace('-', '').replace(' ', '')

        # 公司URL
        companyLink = bsobj.find('a', {'target': '_blank'}, href=re.compile("//www.lagou.com/gongsi/(\d+).html")).attrs['href'].replace('//', '')

        # 公司ID
        companyId = re.findall('\d+', companyLink)[0]
        companyId = int(companyId)

        # 公司名字
        company = re.findall(r'class="fl">\s+(.*?)\s+<i', html.text)[0]

        # 职位描述
        description = ''
        des = bsobj.find('dd', {'class': 'job_bt'}).findAll('p')
        for i in range(len(des)):
            # description.append(des[i].get_text())
            description = description + des[i].get_text() + '\n'

        sql = "insert into lagou_position_info (PositionId, Position, Salary, Publish_time, City, District, BizArea, Address, CompanyId, Company, CompanyLink, Description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cur.execute(sql, (positionId, position, salary, publish_time, city, district, bizArea, address, companyId, company, companyLink,description))
        conn.commit()

    cur.close()
    conn.close()

if __name__ =="__main__":
    position = raw_input("请输入搜索职位：>")
    city = raw_input("请输入城市：>")
    urls = get_information(position, city)
