#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Mercy'
__date__ = '2016-05-25'

from lxml import etree
from math import ceil
import requests
import json
import codecs

import sys
reload(sys)
sys.setdefaultencoding('utf8')

base_url = 'http://www.nstrs.cn/'  # 主域名，用于拼接成完成url
url1 = 'http://www.nstrs.cn/BaogaoLiulan.aspx'  # 第一次请求的url
url2 = 'http://www.nstrs.cn/ashx/baogaoliulan.ashx'  # 第二次请求的url

# 类型（这里可以更改，比如改成‘面上项目’，就爬取面上项目分类的项目）
type = '科学技术部'

# 每页数目
page_size = 10

# 起始页
start_page = 1

# 错误次数
wrong_times = 0


# 请求头部
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Host": "www.nstrs.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"
}


# 读取代理列表
def get_proxy_list():

    proxy_array = []

    # 打开可用代理IP文件
    proxy_file = open('AvailableProxy.txt', 'r')

    # 循环读取，存入数组
    lines = proxy_file.readlines()
    for line in lines:
        proxy_array.append(line.strip())

    # 关闭文件
    proxy_file.close()

    return proxy_array


# 开始爬取
def begin():

    print "---------------------开始爬取---------------------"

    # 打开文件
    output_file = codecs.open('NstrsData.json', mode='wb', encoding='utf-8')  # 存储爬取数据的文件
    failed_url_file = codecs.open('FailedURL.txt', mode='a', encoding='utf-8')  # 存储没有爬取成功的项目详情页的URL地址

    proxy_array = get_proxy_list()
    print "获取可用代理列表，总共 %d 个代理可用" % len(proxy_array)

    print "---使用代理：%s" % proxy_array[0]
    proxies = {}
    proxies['http'] = proxy_array[0]
    del proxy_array[0]
    print "代理列表还剩 %d 个代理可用" % len(proxy_array)

    # 建立会话
    nstrs_session = requests.Session()

    # 发起第一次请求, 返回总的项目数目
    response = nstrs_session.post(url1, headers=headers, data={'action': 'anjihua', 'jihua': type}, proxies=proxies)
    project_count = response.text
    # print project_count
    page_count = int(ceil(float(project_count) / page_size))
    print "第一次请求成功，共有 %d 页， %s 个项目" % (page_count, project_count)

    last_page = start_page
    last_item = 0
    last = crawl(output_file, failed_url_file, nstrs_session, proxies, page_count, last_page, last_item)

    # 循环更换代理，直到没有代理可换或者爬取完成
    while not last == (0, 0):
        if not len(proxy_array) == 0:
            print "---更换代理：%s" % proxy_array[0]
            proxies['http'] = proxy_array[0]
        else:
            print "---------代理用完，没法继续爬，爬取停止---------"
            break
        del proxy_array[0]
        print "代理列表还剩 %d 个代理可用" % len(proxy_array)

        last = crawl(output_file, failed_url_file, nstrs_session, proxies, page_count, last[0], last[1])

    print "---------------------爬取完成---------------------"
    # 关闭文件
    output_file.close()
    failed_url_file.close()


def crawl(output_file, failed_url_file, nstrs_session, proxies, page_count, last_page, last_item):
    # 开始爬取每一页
    for i in range(last_page, page_count+1):

        params = {
            "action": "anjihua",
            "jihua": type,
            "flag": "1",
            "pagesize": str(page_size),
            "pageIndex": str(i)
        }

        # 第二次请求, 返回含有每页的项目列表的html
        try:
            html = nstrs_session.post(url2, headers=headers, data=params, proxies=proxies).text
            tree = etree.HTML(html)
            print "第 %d 页请求成功，下载完成" % i
        except BaseException:
            print "第 %d 页连接异常" % i
            return (i, 0)

        # 存储解析结果
        result_dic = {}

        print "开始爬取第 %d 页所有项目详情" % i
        links = tree.xpath('//tr/td[2]/a/@href')
        for j in range(last_item, len(links)):

            # 中断重启后下一页起始归0
            last_item = 0

            link = base_url + tree.xpath('//tr/td[2]/a/@href')[j]
            print link

            # 请求项目详情页
            try:
                response = nstrs_session.get(link, headers=headers, proxies=proxies, timeout=30)
                html2 = response.text

                # 浏览数超过限制，需要更换代理
                if response.status_code == 200 and len(html2) < 1000:
                    print "---浏览数超过限制，需要更换代理---"
                    return (i, j)

                tree2 = etree.HTML(html2)
            except BaseException:
                print "------URL地址为 %s 的项目没有爬取成功，因为请求不成功------" % link
                # 将没有成功爬取的项目的url地址写入文件，等待下次再爬取
                failed_url_file.write(("%s\n" % link))

                if j == (len(links) - 1):
                    return (i+1, 0)
                else:
                    return (i, j+1)


            # 开始解析
            try:
                result_dic['name'] = tree.xpath('//tr/td[2]/a/text()')[j]
                result_dic['leader'] = tree.xpath('//tr/td[3]/text()')[j]
                result_dic['unit'] = tree.xpath('//tr/td[4]/text()')[j]
                result_dic['projectyear'] = tree.xpath('//tr/td[5]/text()')[j]
                result_dic['url'] = link

                member = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[3]/td[2]/label/text()')
                result_dic['member'] = ''
                for m in member:
                    result_dic['member'] += "".join(m.split())

                abstractCH = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[4]/td[2]/label/text()')[0]
                result_dic['abstractCH'] = "".join(abstractCH.split())

                # 判断是否有“英文摘要”这一栏
                category = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[5]/td[1]/text()')[0].strip()
                if '摘要' in category:
                    abstractEN = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[5]/td[2]/label/text()')[0]
                    keywordCH = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[6]/td[2]/label/text()')[0]
                    keywordEN = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[7]/td[2]/label/text()')[0]
                else:
                    abstractEN = ""
                    keywordCH = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[5]/td[2]/label/text()')[0]
                    keywordEN = tree2.xpath('//div[@class=\'GJKJBG2013_TxtN1\']/table[2]/tr[6]/td[2]/label/text()')[0]

                result_dic['abstractEN'] = " ".join(abstractEN.split())
                result_dic['keywordCH'] = "".join(keywordCH.split())
                result_dic['keywordEN'] = " ".join(keywordEN.split())


            except BaseException as e:
                print "------URL地址为 %s 的项目没有爬取成功，因为解析不成功------" % link
                print "---****错误原因：%s ****------" % e
                # 将没有成功爬取的项目的url地址写入文件，等待下次再爬取
                failed_url_file.write(("%s\n" % link).decode('unicode_escape'))

                # 控制错误次数，适时更换代理，防止一直报错
                global wrong_times
                wrong_times += 1
                if wrong_times == 5:
                    wrong_times = 0
                    print "---解析错误次数过多，需要更换代理---"
                    if j == (len(links) - 1):
                        return (i+1, 0)
                    else:
                        return (i, j+1)

                continue

            # 输出爬取的数据
            project_line = json.dumps(result_dic) + '\n'
            output_file.write(project_line.decode('unicode_escape'))


    # 爬取完成返回(0, 0)
    return (0, 0)

