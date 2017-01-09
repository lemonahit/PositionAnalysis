# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os.path
import threading

headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    }

def proxy_xicidaili(url):
    session = requests.Session()
    page = session.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    taglist = soup.find_all('tr')
    for i in range(1,len(taglist)):
        trtag = taglist[i]
        tdlist = trtag.find_all('td')
        proxy = {'http': tdlist[1].string + ':' + tdlist[2].string,
                 'https': tdlist[1].string + ':' + tdlist[2].string}
        url = "http://ip.chinaz.com/getip.aspx"  # 用来测试IP是否可用的url
        try:
            response = session.get(url, proxies=proxy, timeout=3)
            pro = tdlist[1].string + ':' + tdlist[2].string
            print pro
            with open(filepath, 'a') as fp:
                fp.write(pro+'\n')
        except Exception as e:
            print e
            print proxy, '不能用'
            continue

def proxy_kuaidaili(url):
    response = requests.get(url)
    bsobj = BeautifulSoup(response.text, 'html.parser')
    trlists = bsobj.findAll('tr')
    for i in range(1,len(trlists)):
        ip = trlists[i].find('td', {'data-title': 'IP'}).get_text()
        port = trlists[i].find('td', {'data-title': 'PORT'}).get_text()
        proxy = {'http': ip + ':' + port, 'https': ip + ':' + port}
        url = "http://ip.chinaz.com/getip.aspx"  # 用来测试IP是否可用的url
        try:
            response = requests.get(url, proxies=proxy, timeout=3)
            pro = ip + ':' + port
            print pro
            with open(filepath, 'a') as fp:
                fp.write(pro+'\n')
        except Exception as e:
            print e
            print proxy, '不能用'
            continue

if __name__ == '__main__':
    filepath = '/Users/edz/Documents/project/PositionAnalysis/proxies.txt'

    url1 = 'http://www.xicidaili.com/nn/1'
    url2 = 'http://www.kuaidaili.com/proxylist/1'

    t1 = threading.Thread(target=proxy_xicidaili, args=(url1,))
    t2 = threading.Thread(target=proxy_kuaidaili, args=(url2,))

    t1.start()
    t2.start()
