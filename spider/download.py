# -*- coding:utf-8 -*-

import requests
def download(url, headers):
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
                with open(filename, 'wt') as fn:
                    fn.writelines(proxies[1:])
                return None
            else:
                print "正在使用的IP", proxy
                f.close()
                return html
        except Exception as e:
            print proxy, "此IP已过期"
            with open(filename, 'wt') as fn:
                fn.writelines(proxies[1:])
            f.close()