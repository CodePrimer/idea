# -- coding: utf-8 --

import time
import datetime
import subprocess
import logging
import os


"""Python定时任务"""


class Logger(object):
    def __init__(self, logPath):
        # 创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logPath, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
        fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s %(filename)s[%(funcName)s line:%(lineno)d] %(levelname)s %(message)s",
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


class SysUtil(object):
    """系统工具类"""

    def __init__(self):
        pass

    @staticmethod
    def doCmd(cmdStr, timeOutSeconds=60 * 60):
        """启动应用程序进程 默认超时时间60分钟"""  # TODO windows和Linux系统都支持
        p = subprocess.Popen(cmdStr, close_fds=True)
        tBegin = time.time()
        secondsDelay = 0
        while True:
            if p.poll() is not None:
                break
            secondsDelay = time.time() - tBegin
            if secondsDelay > timeOutSeconds:
                p.kill()
                raise TimeoutError("cmd进程超时" + str(timeOutSeconds) + "s " + cmdStr)
            time.sleep(5)


if __name__ == '__main__':
    # 定时任务:设置固定时间执行cmd指令
    # 执行cmd字符串
    cmd_str = r'copy C:\Users\wangbin\Desktop\abc.rar E:\abc'

    # 在服务器上设置一个log路径，以便后续查询原因
    log_path = r'C:\Users\wangbin\Desktop\a.log'
    logObj = Logger(log_path).get_log

    # 保持后台运行
    while True:
        # 获取系统当前时间
        now_date = datetime.datetime.now()
        # 格式化时间字符串
        date_str = now_date.strftime('%Y-%m-%d %H:%M')
        # 设置运行时间[hh:MM]
        if date_str[11:] == '11:55':
            logObj.info('start do cmd: ' + cmd_str)
            # os.system(cmd_str)
            print('finish cmd.')
            print('finish cmd1.')
            print('finish cmd2.')
            print('finish cmd3.')
            print('finish cmd4.')
            time.sleep(3600)

