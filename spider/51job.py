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
    def __init__(self, jobarea, keyword):
        threading.Thread.__init__(self)
        # self.url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea='+jobarea+'&keyword='+keyword+'&keywordtype=2&curr_page='+str(pn)+'&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
        self.city = jobarea
        self.keyword = keyword
        self.headers = {
            'Host': 'search.51job.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
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
        self.conn()
        f = open(self.filepath, 'a')
        w = csv.writer(f)
        try:
            with self.db.cursor() as cur:
                # for j in range(1,3):
                self.url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea='+self.city+'&keyword='+self.keyword+ '&keywordtype=2&curr_page='+'2'+'&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
                html = download(self.url, self.headers)
                # html = self.session.get(self.url, headers=self.headers)
                html.encoding = 'gbk'
                bsobj = BeautifulSoup(html.text, 'html.parser')
                table = bsobj.find('div', {'class', 'dw_table'})
                all_els = table.findAll('div', {'class', 'el'})
                if all_els:
                    print len(all_els)
                    for i in range(1, len(all_els)):
                        today = all_els[i].find('span', {'class', 't5'}).get_text()
                        if today == self.today:     # 判断发布的职位是否是当天的
                            link = all_els[i].find('a')['href']
                            print link
                            positionId = re.findall(r'\d+', link)[1]
                            s = "SELECT `Position` FROM `51job_position_info` where `PositionId`='" + positionId + "'"
                            if cur.execute(s) == 0:
                                position, salary, area, Description_and_requirements, companyName, companyNature, companyPersonnel, companyIntroduction = self.get_info(link)
                                publish_time = self.today
                                print position, salary, area, companyName
                                # w.writerow([positionId, position, salary, Description_and_requirements, area, publish_time, companyName, companyNature, companyPersonnel, companyIntroduction])
                                try:
                                    sql = "INSERT INTO `51job_position_info` (`PositionId`, `Position`, `Salary`, `Description`, `Address`, `Publish_time`, `Company`, `CompanyNature`, `CompanyPersonnel`, `CompanyIntroduction` ) " \
                                          "VALUE ('"+positionId+"','"+position+"','"+salary+"','"+Description_and_requirements+"','"+area+"','"+publish_time+"','"+companyName+"','"+companyNature+"','"+companyPersonnel+"','"+companyIntroduction+"')"
                                    cur.execute(sql)
                                    self.db.commit()
                                    print sql
                                except Exception as e:
                                    print e
                            else:
                                print positionId + "已存在"
                else:
                    print all_els
        finally:
            f.close()
            self.db.close()

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
            self.headers['Host'] = 'jobs.51job.com'
            html = download(link, self.headers)
            # html = self.session.get(link, headers=self.headers)
            html.encoding = 'gbk'
            bs = BeautifulSoup(html.text, 'html.parser')

            thjob = bs.find('div', {'class', 'tHeader tHjob'})

            cn = thjob.find('div', {'class', 'cn'})
            # 职位
            JobName = cn.find('h1').get_text()
            lname = cn.find('span').get_text()
            if lname == None:
                lname = ''
            # 薪资
            salary = cn.find('strong').get_text()
            if salary == None:
                salary = ''
            infos = bs.find('div', {'class', 'tCompany_main'}).find('div', {'class', 'bmsg job_msg inbox'}).get_text().replace('\t', '').replace('\r', '')
            # sps = bs.findAll('span', {'class', 'sp4'})
            # # 经验要求
            # experience = sps[0].get_text().replace('\n', '')
            # # 学历要求
            # education = sps[1].get_text().replace('\n', '')

            if infos != '':
                if re.findall(r'(.*?)\n', infos)[0] == '':
                #职位描述和任职要求
                    try:
                        Description_and_requirements = re.findall(r'(.*?)\n', infos)[1] + re.findall(r'(.*?)\n', infos)[2]
                    except:
                        Description_and_requirements = ''
                else:
                    try:
                        Description_and_requirements = re.findall(r'(.*?)\n', infos)[0] + re.findall(r'(.*?)\n', infos)[1]
                    except:
                        Description_and_requirements = ''
            else:
                Description_and_requirements = ''

            a = bs.find('div', {'class', 'bmsg inbox'})
            if a != None:
                ar = a.find('p', {'class', 'fp'})
                # 工作地点
                area = lname + '-' + re.findall(r'span>(.*?)<', str(ar))[0].replace('\t', '').decode('utf-8')
            else:
                area = lname

            #公司
            companyName = cn.find('p', {'class', 'cname'}).find('a').get_text()
            if companyName == None:
                companyName = ''
            company = cn.find('p', {'class', 'msg ltype'}).get_text().replace('\r', '').replace('\t', '').replace(' ', '')
            try:
                company = company.decode('utf-8').encode('utf-8')
            except:
                pass
            if company:
                if re.findall(r'(.*?)\xc2\xa0', company) != []:
                    q = re.findall(r'(.*?)\xc2\xa0', company)[0]
                    if re.findall(r'\d', q) == []:
                        # 公司性质
                        companyNature = q
                        if len(re.findall(r'(.*?)\xc2\xa0', company)) > 2:
                            # 公司规模
                            try:
                                companyPersonnel = re.findall(r'(.*?)\xc2\xa0', company)[4]
                            except:
                                companyPersonnel = ''
                        else:
                            companyPersonnel = ''
                    else:
                        companyNature = ''
                        companyPersonnel = q
                else:
                    q = re.findall(r'(.*?)\xa0\xa0', company)[0]
                    if re.findall(r'\d', q) == []:
                        companyNature = q
                        if len(re.findall(r'(.*?)\xa0\xa0', company)) > 2:
                            try:
                                companyPersonnel = re.findall(r'(.*?)\xa0\xa0', company)[2]
                            except:
                                companyPersonnel = ''
                        else:
                            companyPersonnel = ''
                    else:
                        companyNature = ''
                        companyPersonnel = q
            else:
                companyNature = ''
                companyPersonnel = ''

            #公司描述
            try:
                companyIntroduction = bs.find('div', {'class', 'tmsg inbox'}).get_text().replace('\t', '').replace('\n', '')
            except:
                companyIntroduction = ''

            return JobName, salary, area, Description_and_requirements, companyName, companyNature, companyPersonnel, companyIntroduction

        except Exception as e:
            print link
            print e.message


if __name__ == '__main__':
    # filepath = '/Users/edz/Documents/project/PositionAnalysis/positions.csv'
    # if not os.path.isfile(filepath):
    #     f = open(filepath, 'a')
    #     writer = csv.writer(f)
    #     writer.writerow(['positionId', 'position', 'salary', 'Description_and_requirements', 'area', 'publish_time','companyName', 'companyNature', 'companyPersonnel', 'companyIntroduction'])
    #     f.close()
    jobarea = '020000'
    keyword = '大数据'

    Job_qcwy(jobarea, keyword)
