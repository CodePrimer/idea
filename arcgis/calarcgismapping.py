# -*-- coding: UTF-8 -*-

import pickle
import subprocess
import time


def doCmd(cmdStr, timeOutSeconds=60 * 10):
    """启动应用程序进程 默认超时时间10分钟"""  # TODO windows和Linux系统都支持
    p = subprocess.Popen(cmdStr, close_fds=True)
    tBegin = time.time()
    while True:
        if p.poll() is not None:
            break
        secondsDelay = time.time() - tBegin
        if secondsDelay > timeOutSeconds:
            print("cmd进程超时")
            p.kill()
        time.sleep(5)


if __name__ == '__main__':

    mxdPath = r'C:\Users\wangbin\Desktop\arcgisMapping\data\NDVI_City.mxd'
    outPath = r'C:\Users\wangbin\Desktop\arcgisMapping\out\{id}\ndvi_{id}.png'
    # outPath = r'C:\Users\wangbin\Desktop\arcgisMapping\out\ndvi.png'
    replaceLyr = {"tifFile": r'C:\Users\wangbin\Desktop\arcgisMapping\data\ndvi.tif'}
    replaceText = {"date": {"date": u'2020年5月12日'}, "info": {"satellite": "TERRA", "sensor": "MODIS", "resolution": '1000M'}}
    drivenPage = True
    dpi = 300
    outType = '.png'

    saveParam = {'mxdPath': mxdPath,
                 'outPath': outPath,
                 'replaceLyr': replaceLyr,
                 'replaceText': replaceText,
                 'drivenPage': drivenPage,
                 'dpi': dpi,
                 'outType': outType}

    pklPath = r'C:\Users\wangbin\Desktop\abc.pkl'
    f = open(pklPath, 'wb')
    pickle.dump(saveParam, f, protocol=2)
    f.close()

