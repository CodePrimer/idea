# -*- coding: utf-8  -*-
import os
from ftplib import FTP


class MyFtp:

    ftp = FTP()

    def __init__(self, host, port=21):
        self.ftp.connect(host, port)

    def login(self, username, pwd):
        # self.ftp.set_debuglevel(2)  # 打开调试级别2，显示详细信息
        self.ftp.login(username, pwd)
        print(self.ftp.welcome)

    def downloadFile(self, localpath, remotepath, filename):
        os.chdir(localpath)   # 切换工作路径到下载目录
        self.ftp.cwd(remotepath)   # 要登录的ftp目录
        self.ftp.nlst()  # 获取目录下的文件
        file_handle = open(filename, "wb").write   # 以写模式在本地打开文件
        self.ftp.retrbinary('RETR %s' % os.path.basename(filename), file_handle, blocksize=1024)  # 下载ftp文件
        # ftp.delete（filename）  # 删除ftp服务器上的文件

    def close(self):
        self.ftp.set_debuglevel(0)  # 关闭调试
        self.ftp.quit()


if __name__ == '__main__':
    ftp = FTP()
    ftp.connect('192.168.50.75', 21)
    ftp.login('puusadmin', 'Shinetek_fy3')
    print(ftp.welcome)
    root_dir = '/PUUSDATA/NPP/VIIRS/L1/2020/07'     # FTP资源路径
    copy_root_dir = '/data/model/input/satellite/L1B/NPP-VIIRS'
    ftp.cwd(root_dir)
    day_list = ftp.nlst()
    for d in day_list:
        day_path = os.path.join(root_dir, d)
        ftp.cwd(day_path)
        time_list = ftp.nlst()
        for t in time_list:
            if int(t[0:2]) < 11:
                continue
            time_path = os.path.join(day_path, t)
            ftp.cwd(time_path)
            file_list = ftp.nlst(time_path)
            copy_dir = os.path.join(copy_root_dir, '202007' + d + t)
            os.mkdir(copy_dir)
            for f in file_list:
                copy_file_path = os.path.join(copy_dir, os.path.basename(f))
                file_handle = open(copy_file_path, "wb").write
                ftp.retrbinary('RETR %s' % os.path.basename(f), file_handle, blocksize=1024)  # 下载ftp文件
                print('Finish Copy: %s' % copy_file_path)
    ftp.quit()

    print('finish')