# -*- coding: utf-8 -*-
# @Time : 2020/8/10 13:27
# @Author : wangbin

import os
import sys
import logging
from GF1 import GF


class Logger(object):
    def __init__(self, logPath):
        # 创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logPath, mode='w', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
        fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            "%(asctime)s %(filename)s[%(funcName)s line:%(lineno)d] %(levelname)s %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @property
    def get_log(self):
        """定义一个函数，回调logger实例"""
        return self.logger


if __name__ == '__main__':

    rootDir = sys.argv[1]
    outDir = sys.argv[2]
    # inputDir = r'E:\Data\GF'
    # outputDir = r'C:\Users\Administrator\Desktop\output'
    logPath = os.path.join(os.path.dirname(__file__), os.path.basename(__file__).split('.')[0] + ".log")
    logObj = Logger(logPath).get_log

    if not os.path.exists(rootDir):
        print('输入文件夹不存在')
        exit(0)

    count = 0
    for f in os.listdir(rootDir):
        # 过滤文件夹
        inputDir = os.path.join(rootDir, f)
        outputDir = os.path.join(outDir, f)
        if not os.path.isdir(inputDir):
            continue
        else:
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
            count += 1
            logObj.info('Start Process' + str(count) + ':' + f)
            GF.main(inputDir, outputDir)
