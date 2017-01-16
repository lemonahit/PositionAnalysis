# -*- coding:utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import threading
import datetime
from bs4 import BeautifulSoup
import requests
import re
import pymysql
from download import download
import csv


class Job_qcwy(threading.Thread):
    def __init__(self, jobarea):
        threading.Thread.__init__(self)
        # self.url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea='+jobarea+'&keyword='+keyword+'&keywordtype=2&curr_page='+str(pn)+'&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
        self.city = jobarea
        self.keywords = ['python', '大数据', '']
        self.headers = {
            'Host': 'search.51job.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        self.filepath = '/Users/edz/Documents/project/PositionAnalysis/positions.csv'
        # self.data = {
        #         'fromJs': 1,
        #         'jobarea': jobarea,
        #         'funtype': '',
        #         'industrytype': '',
        #         'keyword': keyword,
        #         'keywordtype': 2,
        #         'lang': 'c',
        #         'stype': 2,
        #         'postchannel': 0000,
        #         'fromType': 1,
        #         'confirmdate': 9,
        #         'curr_page': pn
        #     }
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
        # self.conn()
        f = open(self.filepath, 'a')
        w = csv.writer(f)
        try:
            # with self.db.cursor() as cur:
            for i in range(len(self.keywords)):
                for j in range(1,2):
                    self.url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea='+self.city+'&keyword='+self.keywords[i]+\
                               '&keywordtype=2&curr_page='+str(j)+'&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
                    # html = download(self.url, self.headers)
                    html = self.session.get(self.url, headers=self.headers)
                    html.encoding = 'gbk'
                    bsobj = BeautifulSoup(html.text, 'html.parser')
                    table = bsobj.find('div', {'class', 'dw_table'})
                    all_els = table.findAll('div', {'class', 'el'})
                    for i in range(1, len(all_els)):
                        today = all_els[i].find('span', {'class', 't5'}).get_text()
                        if today == self.today:     # 判断发布的职位是否是当天的
                            link = all_els[i].find('a')['href']
                            position, salary, area, Description_and_requirements, companyName, companyNature, companyPersonnel, companyIntroduction = self.get_info(link)
                            positionId = re.findall(r'\d+', link)[1]
                            publish_time = self.today
                            print position, companyName
                            w.writerow([positionId, position, salary, Description_and_requirements, area, publish_time, companyName, companyNature, companyPersonnel, companyIntroduction])
                                # sql = "INSERT INTO `` () VALUE ()"
                                # cur.execute(sql)
                                # self.db.commit()
        finally:
            f.close()
            # self.db.close()

    # 数据库设置
    def conn(self):
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='PositionAnalysis',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    # 获取职位的详细信息
    def get_info(self, link):
        try:
            # html = download(link, self.headers)
            html = self.session.get(link, headers=self.headers)
            html.encoding = 'gbk'
            bs = BeautifulSoup(html.text, 'html.parser')

            thjob = bs.find('div', {'class', 'tHeader tHjob'})

            cn = thjob.find('div', {'class', 'cn'})
            JobName = cn.find('h1').get_text()
            lname = cn.find('span').get_text()
            salary = cn.find('strong').get_text()
            infos = bs.find('div', {'class', 'tCompany_main'}).find('div', {'class', 'bmsg job_msg inbox'}).get_text().replace('\t', '')
            #职位描述
            Description_and_requirements = re.findall(r'(.*?)\r\n', infos)[0] + re.findall(r'(.*?)\r\n', infos)[1]

            a = bs.find('div', {'class', 'bmsg inbox'}).find('p', {'class', 'fp'})
            area = lname + '-' + re.findall(r'span>(.*?)<', str(a))[0].replace('\t', '')

            #公司
            companyName = cn.find('p', {'class', 'cname'}).find('a').get_text()
            company = cn.find('p', {'class', 'msg ltype'}).get_text().replace('\r', '').replace('\t', '').replace(' ', '')
            company = company.decode('utf-8').encode('utf-8')
            companyNature = re.findall(r'(.*?)\xc2\xa0', company)[0]
            companyPersonnel = re.findall(r'(.*?)\xc2\xa0', company)[4]
            #公司描述
            companyIntroduction = bs.find('div', {'class', 'tmsg inbox'}).get_text().replace('\t', '').replace('\n', '')

            return JobName, salary, area, Description_and_requirements, companyName, companyNature, companyPersonnel, companyIntroduction

        except Exception as e:
            print e.message


if __name__ == '__main__':
    filepath = '/Users/edz/Documents/project/PositionAnalysis/positions.csv'
    if not os.path.isfile(filepath):
        f = open(filepath, 'a')
        writer = csv.writer(f)
        writer.writerow(['positionId', 'position', 'salary', 'Description_and_requirements', 'area', 'publish_time','companyName', 'companyNature', 'companyPersonnel', 'companyIntroduction'])
        f.close()
    jobarea = ['010000','020000']

    threads = []

    for i in range(len(jobarea)):
        t = Job_qcwy(jobarea[i])
        threads.append(t)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
