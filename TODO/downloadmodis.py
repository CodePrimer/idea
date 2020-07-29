from selenium import webdriver
import time
import datetime
import os
from BaseUtil import BaseUtil
import requests
from bs4 import BeautifulSoup

"""MODIS产品数据下载"""


def timeDelay(old_date_str):
    # 往前推算一天
    old_datetime = datetime.datetime.strptime(old_date_str, "%Y.%m.%d")
    new_datetime = old_datetime + datetime.timedelta(days=-1)
    new_date_str = new_datetime.strftime("%Y.%m.%d")
    return new_date_str


def DayCount(dt):
    year = int(dt.split(".")[0])
    month = int(dt.split(".")[1])
    day = int(dt.split(".")[2])
    standard_date = datetime.date(year, month, day)
    # January 1st
    start_date = datetime.date(year, 1, 1)
    # days
    daycount = (standard_date - start_date).days + 1
    return daycount


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


def search_file(url, regionList):

    demo = getHTMLText(url)

    # 解析HTML代码
    soup = BeautifulSoup(demo, 'html.parser')

    # 模糊搜索HTML代码的所有包含href属性的<a>标签
    a_labels = soup.find_all('a', attrs={'href': True})

    # 获取所有<a>标签中的href对应的值，即超链接
    file_name = []
    for a in a_labels:
        herf_str = a.get('href')
        if herf_str.endswith(".hdf"):
            region_code = herf_str.split(".")[2]
            if region_code in regionList:
                file_name.append(herf_str)
    return file_name


def main():

    # url_base = "https://e4ftl01.cr.usgs.gov/MOLA/MYD11A1.006/"
    url_base = "https://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.006/"

    driver = webdriver.Chrome(r"C:\Program Files (x86)\Google\Chrome\Driven\chromedriver.exe")

    downloadDir = r"C:\Users\wangbin\Downloads"

    # 第一次手动输入密码
    url_test = "https://e4ftl01.cr.usgs.gov/MOLA/MYD11A1.006/2002.07.04/MYD11A1.A2002185.h02v09.006.2015146150721.hdf"
    driver.get(url_test)

    # 按照指定年月日往前下载
    first_date_str = "2020.04.20"

    download_day_num = 1

    old_date_str = first_date_str
    for i in range(download_day_num):
        # 执行老日期任务
        print("start download: ", old_date_str)

        day_count = DayCount(old_date_str)
        url_day = url_base + old_date_str + "/"
        # regionList = ["h26v06", "h27v06"] # 云南
        regionList = ["h25v05", "h26v05"]   # 青海
        file_name = search_file(url_day, regionList)

        # 创建文件夹
        dir_path = os.path.join(downloadDir, old_date_str)
        BaseUtil.create_dir(dir_path)

        # 下载文件
        for f in file_name:
            url_file = url_day + f
            driver.get(url_file)
            # 等待文件下载完成
            tBegin = time.time()
            secondsDelay = 0
            while True:
                file_path = os.path.join(downloadDir, f)
                if BaseUtil.is_file(file_path):
                    BaseUtil.copy_file(file_path, dir_path)
                    if BaseUtil.is_file(os.path.join(dir_path, f)):
                        time.sleep(3)
                        os.remove(file_path)
                    break
                else:
                    time.sleep(2)
                secondsDelay = time.time() - tBegin
                if secondsDelay > 600:
                    print("Download outTime: " + f)
                    break

        new_date_str = timeDelay(old_date_str)
        # 更换老日期字符串
        old_date_str = new_date_str

    print("finish.")


if __name__ == "__main__":

    main()
