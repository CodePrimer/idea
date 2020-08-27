# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: WangBin -*-

import os
import time


class BaseUtil(object):
    """基础操作类"""

    def __init__(self):
        pass

    @staticmethod
    def fileName(filePath, ext=True):
        """
        获取文件名
        :param filePath: 文件路径 # TODO 文件夹路径如何过滤
        :param ext: True-返回值带文件类型 False-返回值不带文件类型
        :return: str
        """
        baseName = os.path.basename(filePath)
        if not ext:
            splitList = baseName.split(".")
            splitList.pop()
            return ".".join(splitList)
        else:
            return baseName

    @staticmethod
    def fileExt(filePath):
        """
        获取文件扩展类型
        :param filePath: 文件路径 # TODO 文件夹路径如何过滤
        :return:str
        """
        filename = os.path.basename(filePath)
        splitList = filename.split(".")
        if len(splitList) < 2:
            print("输入文件名有误.")
            return None
        else:
            return splitList[-1]

    @staticmethod
    def timeStamp():
        """
        返回当前时间戳
        :return: 12位字符串
        """
        return str(int(time.time() * 100))

    @staticmethod
    def fileNameAddStamp(fileName, ext=True):
        """
        将输入文件名添加时间戳返回
        :param fileName: 输入文件名
        :param ext: 文件名是否带后缀
        :return: 添加上时间戳的文件名
        """
        splitList = fileName.split(".")
        if len(splitList) < 2:
            print("输入文件名有误.")
            return None
        if ext:
            splitList = fileName.split(".")
            extStr = splitList[-1]
            splitList.pop()
            nameStr = ".".join(splitList)
            fileNameStamp = nameStr + "_" + BaseUtil.timeStamp() + "." + extStr
        else:
            fileNameStamp = fileName + BaseUtil.timeStamp()
        return fileNameStamp

