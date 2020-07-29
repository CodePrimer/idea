# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-

import os
import time
from urllib import request


"""CIMISS数据下载"""

if __name__ == "__main__":
    dir_path = r"C:\Users\Administrator\Desktop\cimissdownload\downloads"
    # dir_path = r"C:\Users\wangbin\Desktop\downloads"
    file_list = os.listdir(dir_path)

    download_list = []
    for f in file_list:
        file_path = os.path.join(dir_path, f)
        size_byte = os.path.getsize(file_path)
        if size_byte/1024 < 10:
            os.remove(file_path)
            download_list.append(f.split(".")[0])
    print(download_list)

    hosturl = "http://10.208.121.55/cimiss-web/api"
    outdir = r"C:\Users\Administrator\Desktop\cimissdownload\downloads"
    for timeStr in download_list:
        fmt = "%Y%m%d%H%M%S"
        # timestamp = time.mktime(time.strptime(startTime, fmt)) + 60 * 60 * 24 * i
        # timeStr = time.strftime(fmt, time.localtime(timestamp))
        # argument dict
        args = {"userId": "BEKM_CC_lmhl",
                "pwd": "lmhl123",
                "interfaceId": "getSurfEleByTime",
                "dataCode": "SURF_CHN_MUL_DAY",
                "elements": "Station_Id_C,Station_Id_d,Lat,Lon,Year,Mon,Day,EVP,SSH",
                "times": timeStr,
                "dataFormat": "csv"}

        targetUrl = hosturl + "?"
        paramList = []
        for key in args.keys():
            str = key + "=" + args[key]
            paramList.append(str)
        targetUrl += "&".join(paramList)
        print(targetUrl)

        req = request.Request(targetUrl)
        req.add_header('User-Agent',
                       'Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)) Chrom/80.0.3987.132 Safari/537.36')
        with request.urlopen(req) as f:
            data = f.read().decode("utf-8")

        saveFile = os.path.join(outdir, timeStr + ".txt")
        with open(saveFile, "w") as f:
            dataFrame = data.split("\r\n")
            for line in dataFrame:
                f.write(line + "\n")
        print("finish:" + timeStr)
        time.sleep(1)
    print("finish")