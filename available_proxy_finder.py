#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Mercy'
__date__ = '2016-05-25'

import urllib2
import threading

# 标识可用代理处理是否已完成
isFinished = False

# 用来测试代理是否可用的URL地址
url = 'http://www.nstrs.cn/BaogaoLiulan.aspx'

def find_available(lock, inFile, outFile):
    # 读取一行代理
    lock.acquire()
    line = inFile.readline().strip()
    lock.release()

    protocol = line.split('://')[0]
    try:
        proxy_support = urllib2.ProxyHandler({protocol: line})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        request = urllib2.Request(url)
        content = urllib2.urlopen(request, timeout=20).read()

        if not content == "":
            lock.acquire()
            print '#####添加可用代理：', line
            outFile.write('%s\n' % line)
            lock.release()
        else:
            print '此行代理无效！！'

    except Exception, error:
        print "此行代理无效！！,错误原因:", error



def find():

    # 打开文件
    inFile = open('Proxy.txt', 'r')
    outFile = open('AvailableProxy.txt', 'w')

    lock = threading.Lock()

    # 启动线程
    all_thread = []
    for i in range(500):
        t = threading.Thread(target=find_available, args=(lock, inFile, outFile))
        all_thread.append(t)
        t.start()

    # 阻塞线程
    for t in all_thread:
        t.join()

    # 关闭文件
    inFile.close()
    outFile.close()

    # 设置可用代理处理完成
    global isFinished
    isFinished = True