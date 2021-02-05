# -*- coding: utf-8 -*-

"""
下载周杰伦所有歌曲
https://myfreemp3.vip/cn    # 免费下歌网址

https://www.bilibili.com/video/BV1fx411N7bU?from=search&seid=3210960788106909734    # 周杰伦歌曲列表获取

"""

import re
import os
import requests
from bs4 import BeautifulSoup
import pymysql
import uuid


def getHTMLText(url):
    try:
        # 获取服务器的响应内容，并设置最大请求时间
        res = requests.get(url, timeout=15)
        # 判断返回状态码是否为200
        res.raise_for_status()
        # 设置该html文档可能的编码
        res.encoding = res.apparent_encoding
        # 返回网页HTML代码
        return res.text
    except:
        return


def readInfo():
    filename = r'C:\Users\Administrator\Desktop\temp\周杰伦 - 完美主义.mp3'
    fsock = open(filename, "rb", 0)  # 打开文件
    fsock.seek(-128, 2)
    tagdata = fsock.read(128)  # 读取128字节的数据

    if tagdata[:3] == "TAG":  # 判断是否是有效的含Tag的MP3文件
        # # 循环取出Tag信息位置信息， 如3, 33, stripnulls，并依次赋给start, end, parseFunc
        # for tag, (start, end, parseFunc) in self.tagDataMap.items():
        #     # tagdata[start:end]读出start到end的字节，使用parseFunc处理这些内容
        #     self[tag] = parseFunc(tagdata[start:end])
        pass

    fsock.close()  # 关闭文件，注意在finally中，出错也需要关闭文件句柄


if __name__ == '__main__':

    dirPath = 'F:/周杰伦'
    for fileName in os.listdir(dirPath):
        newFileName = fileName.replace(' myfreemp3.vip ', '')
        os.rename(os.path.join(dirPath, fileName), os.path.join(dirPath, newFileName))
        # print(fileName)

    # 数据库操作
    conn = pymysql.connect(
        db='mymusic',
        user='root',
        password='ISKYpwd@1',
        host='10.16.56.6',
        port=3306
    )

    cursor = conn.cursor()
    sqlStr = ''
    sqlData = ()
    cursor.execute(sqlStr, sqlData)
    conn.commit()
    cursor.close()
    conn.close()

    print('Finish')
