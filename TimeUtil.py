# -*- coding: utf-8  -*-
# -*- author: htht -*-

import time
import datetime


class TimeUtil(object):
    """
    时间信息操作类，主要实现
    1.datetime,str,timestamp三种类型相互转换
    2.timedelta时间计算
    """

    def __init__(self):
        pass

    @staticmethod
    def timestamp():
        """
        返回当前时间戳 12位
        :return: str:
        """
        return str(int(time.time() * 100))

    @staticmethod
    def str_to_timestamp(string, fmt):
        """
        字符串转为时间戳
        :param string: str: 输入字符串
        :param fmt: str: 格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :return: float: 时间戳 单位：秒
        """
        return time.mktime(time.strptime(string, fmt))

    @staticmethod
    def timestamp_to_str(ts, fmt):
        """
        时间戳转为字符串
        :param ts: float: 时间戳 单位：秒
        :param fmt: str: 格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :return: str:
        """
        return time.strftime(fmt, time.localtime(ts))

    @staticmethod
    def str_to_datetime(string, fmt):
        """
        字符串转为datetime类型
        :param string: str: 输入字符串
        :param fmt: str: 格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :return: datetime:
        """
        return datetime.datetime.strptime(string, fmt)

    @staticmethod
    def datetime_to_str(dt, fmt):
        """
        datetime类型转换为字符串
        :param dt: datetime
        :param fmt: str: 格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :return: str:
        """
        return dt.strftime(fmt)

    @staticmethod
    def time_delta(string, fmt, delta_sec):
        """
        对输入时间字符串计算时间推移输出新时间字符串
        :param string: str: 推移前时间字符串
        :param fmt: str: 输入格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :param delta_sec: float: 推移时间，正值向后推移，负值向前推移，单位 秒。
        :return: str: 推移后时间字符串
        """
        old_stamp = time.mktime(time.strptime(string, fmt))
        new_stamp = old_stamp + delta_sec
        return time.strftime(fmt, time.localtime(new_stamp))

    @staticmethod
    def day_of_year(string, fmt):
        """
        对输入时间字符串判断是该年中的第几天
        :param string: str: 输入时间字符串
        :param fmt: 输入格式化字符串  e.g: "%Y-%m-%d %H:%M:%S"
        :return: str: 三位天数字符串  e.g: '032'
        """
        dt = datetime.datetime.strptime(string, fmt)
        return dt.strftime("%j")


if __name__ == "__main__":

    # 常用代码
    # 1.年日转月日
    # issue = "2020-032"
    # a = TimeUtil.str_to_datetime(issue, "%Y-%j")
    # b = TimeUtil.datetime_to_str(a, "%Y-%m-%d")

    # 1.年日转月日
    dt = datetime.datetime.strptime("2020032", "%Y%j")
    print(dt.strftime("%Y-%m-%d"))
    print("finish")
