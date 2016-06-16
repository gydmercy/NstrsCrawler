#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Mercy'
__date__ = '2016-06-12'


import proxy_fetcher
import available_proxy_finder
import nstrs_crawler


def run():
    print "++++++++++++++++++++++++ Step_1 获取代理 +++++++++++++++++++++++"
    proxy_fetcher.fetch()

    print "++++++++++++++++++++++++ Step_2 获取其中的可用代理 ++++++++++++++"
    available_proxy_finder.find()

    # 阻塞主线程，等待可用代理处理完毕
    while not available_proxy_finder.isFinished:
        pass

    print "++++++++++++++++++++++++ Step_3 启动爬虫 +++++++++++++++++++++++"
    nstrs_crawler.begin()


# 主函数
if __name__ == '__main__':
    run()