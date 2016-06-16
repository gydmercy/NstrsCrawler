#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Mercy'
__date__ = '2016-05-25'

import urllib2
from BeautifulSoup import BeautifulSoup

def fetch():
    # 打开文件，存储代理数据
    of = open('Proxy.txt', 'wb')

    for page in range(1,10):
        url = 'http://www.xicidaili.com/nn/%s' %page
        user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"

        # 发起请求
        request = urllib2.Request(url)
        request.add_header("User-Agent", user_agent)
        content = urllib2.urlopen(request)

        # 解析
        soup = BeautifulSoup(content)
        trs = soup.find('table', {"id":"ip_list"}).findAll('tr')

        for tr in trs[1:]:
            tds = tr.findAll('td')

            # 解析获得 ip,port,protocol
            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            protocol = tds[5].text.strip()

            # 写入文件
            if protocol == 'HTTP' or protocol == 'HTTPS':
                of.write('%s://%s:%s\n' % (protocol.lower(), ip, port))
                print '%s://%s:%s' % (protocol.lower(), ip, port)

    # 关闭文件
    of.close()
