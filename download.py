# -*- coding:utf-8 -*-

import requests
def download(url, headers):
    # headers = {
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
    # }

    # headers = [
    #     "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    #     "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    #     "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
    #     ]

    while True:
        session = requests.Session()
        filename = '/Users/edz/Documents/project/PositionAnalysis/proxies.txt'
        f = open(filename,'r')
        proxies = f.readlines()
        if len(proxies) != 0:
            proxy = {'http': proxies[0].replace('\n', ''), 'https': proxies[0].replace('\n', '')}
        try:
            html = session.get(url, proxies=proxy, headers=headers, timeout=3)
            if 400 <= html.status_code <= 600:
                with open('proxies.txt', 'wt') as fn:
                    fn.writelines(proxies[1:])
                return None
            else:
                print "正在使用的IP", proxy
                f.close()
                return html
        except Exception as e:
            print proxy, "此IP已过期"
            with open('proxies.txt', 'wt') as fn:
                fn.writelines(proxies[1:])
            f.close()