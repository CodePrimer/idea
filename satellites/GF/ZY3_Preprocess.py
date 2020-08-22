# -*- coding: utf-8 -*-
# @Time : 2020/8/10 13:27
# @Author : wangbin

import os
import re
import json
import time
import shutil
import logging
import zipfile
import tarfile
import datetime
import xml.dom.minidom

import gdal
from unrar import rarfile


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


class ZY3(object):

    # 辐射定标参数文件
    RAD_CORRECT_PARAM = os.path.join(os.path.dirname(__file__), 'RadCorrectParam_ZY3.json')
    SIXS_EXE = os.path.join(os.path.dirname(__file__), '6S', '6s.exe')
    FILE_SUFFIX = {'ZY3_MUX': ''}
    WAVE_RANGE = [[0.45, 0.52],
                  [0.52, 0.59],
                  [0.63, 0.69],
                  [0.77, 0.89]]

    def __init__(self, inputPath, tempDir, outputPath, logPath=None):
        # 输入信息
        self.inputPath = inputPath  # str:输入文件路径
        self.tempDir = tempDir  # str:临时文件夹路径
        self.basename = None  # str:文件基础名(不带后缀)
        self.ext = None  # str:文件后缀名 (一般为.zip和.tar.gz)
        self.fileType = None  # str:文件类型，有可能出现文件后缀和类型不匹配现象 .rar
        self.satellite = None  # str:卫星类型
        self.sensor = None  # str:传感器类型
        self.longitude = None  # str:影像中心经度
        self.latitude = None  # str:影像中心纬度
        self.year = None  # str:影像获取时间-年
        self.month = None  # str:影像获取时间-月
        self.day = None  # str:影像获取时间-日
        self.logPath = logPath  # str:日志文件路径
        self.logObj = None  # str:日志文件对象

        # 中间数据
        self.uncompressDir = None   # 解压文件夹根目录
        self.uncompressFile = {}  # dict:解压后文件清单 格式: {'文件名': {'path': '文件全路径'}, 'type': '镜头名', 'ext': '文件后缀名' }
        self.radCorrectParam = {}   # dict:辐射定标参数 {'gain':[], 'offset':[]}
        self.atmCorrectParam = {}   # dict:6s大气校正参数 {'xa': [], 'xb': [], 'xc': []}
        self.noProjTifPath = None   # 中间生成的未投影文件路径
        self.rpcCopyPath = None     # 复制rpb文件路径
        self.centerTime = None
        # 输出信息
        self.outputPath = outputPath  # str:输出文件路径

    def doInit(self):
        """
        类对象初始化操作
        1.初始化Log文件
        2.有效性检查
            2.1 输入文件是否存在
            2.2 输入文件名正则是否符合规则
            2.3 创建临时文件夹
        3.获取文件基本信息
        """

        # 1.初始化Log文件
        if self.logPath is None:
            self.logPath = os.path.join(os.path.dirname(__file__), os.path.basename(__file__).split('.')[0] + ".log")
        else:
            logDir = os.path.dirname(self.logPath)
            try:
                if not os.path.isdir(logDir):
                    os.makedirs(logDir)
            except Exception as e:
                print(e)
                return False
        self.logObj = Logger(self.logPath).get_log

        # 2.有效性检查
        # 2.1 输入文件是否存在
        if not os.path.exists(self.inputPath):
            self.logObj.error("输入文件不存在！")
            return False
        # 2.2 输入文件名正则是否符合规则 TODO 暂时只做下划线分割长度判断
        if self.inputPath.endswith('.zip'):
            self.basename = os.path.basename(self.inputPath).replace('.zip', '')
            self.ext = '.zip'
        elif self.inputPath.endswith('.tar.gz'):
            self.basename = os.path.basename(self.inputPath).replace('.tar.gz', '')
            self.ext = '.tar.gz'
        elif self.inputPath.endswith('.tar'):
            self.basename = os.path.basename(self.inputPath).replace('.tar', '')
            self.ext = '.tar'
        else:
            self.logObj.error("未知的文件格式！")
            return False
        filenameInfo = self.basename.split('_')
        if len(filenameInfo) != 6:
            self.logObj.error("文件名格式错误！")
            return False
        # 2.3 创建临时文件夹
        try:
            if not os.path.isdir(self.tempDir):
                os.makedirs(self.tempDir)
        except Exception as e:
            self.logObj.error("创建临时文件失败！")
            return False

        # 3.获取文件基本信息
        self.satellite = filenameInfo[0]
        self.sensor = filenameInfo[1]
        self.longitude = filenameInfo[2]
        self.latitude = filenameInfo[3]
        self.year = filenameInfo[4][0:4]
        self.month = filenameInfo[4][4:6]
        self.day = filenameInfo[4][6:8]

        return True

    def uncompress(self):
        """解压缩文件"""
        self.uncompressDir = os.path.join(self.tempDir, self.basename)
        if zipfile.is_zipfile(self.inputPath):
            self.logObj.info("压缩文件格式为zip，开始解压...")
            zFile = zipfile.ZipFile(self.inputPath, 'r')
            for f in zFile.namelist():
                zFile.extract(f, self.uncompressDir)
                self.uncompressFile[f] = {'path': os.path.join(self.uncompressDir, f),
                                          'ext': os.path.splitext(f)[1],
                                          'type': f.replace(self.basename, '').replace(os.path.splitext(f)[1], '')
                                          }
        elif tarfile.is_tarfile(self.inputPath):
            self.logObj.info("压缩文件格式为tar，开始解压...")
            tFile = tarfile.open(self.inputPath)
            for f in tFile.getnames():
                tFile.extract(f, self.uncompressDir)
                self.uncompressFile[f] = {'path': os.path.join(self.uncompressDir, f),
                                          'ext': os.path.splitext(f)[1],
                                          'type': f.replace(self.basename, '').replace(os.path.splitext(f)[1], '')
                                          }
        elif rarfile.is_rarfile(self.inputPath):
            self.logObj.info("压缩文件格式为rar，开始解压...")
            rFile = rarfile.RarFile(self.inputPath, mode='r')
            for f in rFile.namelist():
                rFile.extract(f, self.uncompressDir)
                self.uncompressFile[f] = {'path': os.path.join(self.uncompressDir, f),
                                          'ext': os.path.splitext(f)[1],
                                          'type': f.replace(self.basename, '').replace(os.path.splitext(f)[1], '')
                                          }
        else:
            self.logObj.error("无法识别的压缩文件格式！")
            return False
        self.logObj.info("解压缩文件成功.")

    def radiometricCorrection(self):
        """辐射定标，为了减少IO这里先获取辐射定标参数"""
        radJsonFile = ZY3.RAD_CORRECT_PARAM
        jsonData = json.load(open(radJsonFile))
        if self.year in jsonData[self.satellite][self.sensor].keys():
            param = jsonData[self.satellite][self.sensor][self.year]
        else:
            param = jsonData[self.satellite][self.sensor]['latest']
        self.radCorrectParam = param
        self.logObj.info("获取辐射定标参数成功...")

    def atmosphericCorrection(self):
        """获取大气校正参数并进行计算"""
        # 不同卫星传感器解压后多余的文件后缀
        satSor = self.satellite + '_' + self.sensor
        if satSor not in ZY3.FILE_SUFFIX.keys():
            self.logObj.error("无法识别的卫星传感器标识！")
            return False
        xmlName = self.basename + ZY3.FILE_SUFFIX[satSor] + '.xml'
        if xmlName not in self.uncompressFile.keys():
            self.logObj.error("未找到对应xml文件！")
            return False
        xmlPath = self.uncompressFile[xmlName]['path']
        # 解析xml获取大气校正所需参数
        dom = xml.dom.minidom.parse(xmlPath)
        root = dom.documentElement
        CenterTimeNode = root.getElementsByTagName('CenterTime')[0]
        CenterTime = CenterTimeNode.childNodes[0].data
        self.centerTime = CenterTime
        month = int(CenterTime.split(' ')[0].split('-')[1])
        day = int(CenterTime.split(' ')[0].split('-')[2])
        TopLeftLatitudeNode = root.getElementsByTagName('TopLeftLatitude')[0]
        TopLeftLatitude = float(TopLeftLatitudeNode.childNodes[0].data)
        TopLeftLongitudeNode = root.getElementsByTagName('TopLeftLongitude')[0]
        TopLeftLongitude = float(TopLeftLongitudeNode.childNodes[0].data)
        TopRightLatitudeNode = root.getElementsByTagName('TopRightLatitude')[0]
        TopRightLatitude = float(TopRightLatitudeNode.childNodes[0].data)
        TopRightLongitudeNode = root.getElementsByTagName('TopRightLongitude')[0]
        TopRightLongitude = float(TopRightLongitudeNode.childNodes[0].data)
        BottomRightLatitudeNode = root.getElementsByTagName('BottomRightLatitude')[0]
        BottomRightLatitude = float(BottomRightLatitudeNode.childNodes[0].data)
        BottomRightLongitudeNode = root.getElementsByTagName('BottomRightLongitude')[0]
        BottomRightLongitude = float(BottomRightLongitudeNode.childNodes[0].data)
        BottomLeftLatitudeNode = root.getElementsByTagName('BottomLeftLatitude')[0]
        BottomLeftLatitude = float(BottomLeftLatitudeNode.childNodes[0].data)
        BottomLeftLongitudeNode = root.getElementsByTagName('BottomLeftLongitude')[0]
        BottomLeftLongitude = float(BottomLeftLongitudeNode.childNodes[0].data)
        maxLat = max([TopLeftLatitude, TopRightLatitude, BottomRightLatitude, BottomLeftLatitude])
        minLat = min([TopLeftLatitude, TopRightLatitude, BottomRightLatitude, BottomLeftLatitude])
        maxLon = max(
            [TopLeftLongitude, TopRightLongitude, BottomRightLongitude, BottomLeftLongitude])
        minLon = min(
            [TopLeftLongitude, TopRightLongitude, BottomRightLongitude, BottomLeftLongitude])
        centerLat = (maxLat + minLat) / 2
        centerLon = (maxLon + minLon) / 2

        # 太阳方位角
        SolarAzimuthNode = root.getElementsByTagName('SolarAzimuth')[0]
        SolarAzimuth = float(SolarAzimuthNode.childNodes[0].data)
        # 太阳天顶角
        SolarZenithNode = root.getElementsByTagName('SolarZenith')[0]
        SolarZenith = float(SolarZenithNode.childNodes[0].data)
        # 卫星方位角
        SatelliteAzimuthNode = root.getElementsByTagName('SatelliteAzimuth')[0]
        SatelliteAzimuth = float(SatelliteAzimuthNode.childNodes[0].data)
        # 卫星天顶角
        SatelliteZenithNode = root.getElementsByTagName('SatelliteZenith')[0]
        SatelliteZenith = float(SatelliteZenithNode.childNodes[0].data)

        self.atmCorrectParam['xa'] = []
        self.atmCorrectParam['xb'] = []
        self.atmCorrectParam['xc'] = []
        for i in range(4):
            xa, xb, xc = self.getSixsParams(month, day, SolarZenith, SolarAzimuth, SatelliteZenith, SatelliteAzimuth,
                                            centerLon, centerLat, ZY3.WAVE_RANGE[i])
            self.atmCorrectParam['xa'].append(xa)
            self.atmCorrectParam['xb'].append(xb)
            self.atmCorrectParam['xc'].append(xc)
        self.logObj.info("获取6S大气校正参数成功...")

    def getSixsParams(self, mm, dd, SolarZenith, SolarAzimuth, SatelliteZenith, SatelliteAzimuth, lon, lat, wave):
        igeom = '0\n'
        asol = str(SolarZenith) + '\n'
        phio = str(SolarAzimuth) + '\n'
        avis = str(SatelliteZenith) + '\n'      # TODO 看一下值
        phiv = str(SatelliteAzimuth) + '\n'
        month = str(mm) + '\n'
        jday = str(dd) + '\n'
        if 4 < mm < 9:      # TODO 未进行地理位置判断
            idatm = '2\n'
        else:
            idatm = '3\n'
        iaer = '3\n'        # TODO 默认城市型
        v = '40\n'          # 默认能见度为40km 与FLASSH模型一致
        xps = '0.05\n'      # TODO 默认固定海拔
        xpp = '-1000\n'
        iwave = '-2\n'
        wlinf = str(wave[0]) + '\n'
        wlsup = str(wave[1]) + '\n'
        inhome = '0\n'
        idirect = '0\n'
        igroun = '1\n'
        rapp = '0\n'
        file_content = [igeom, asol, phio, avis, phiv, month, jday, idatm, iaer, v, xps, xpp, iwave, wlinf, wlsup,
                        inhome, idirect, igroun, rapp]
        in_txt = os.path.join(os.path.dirname(ZY3.SIXS_EXE), 'in.txt')
        in_txt = in_txt.replace('\\', '/')
        with open(in_txt, 'w') as (f):
            f.writelines(file_content)
        out_txt = os.path.join(os.path.dirname(ZY3.SIXS_EXE), 'sixs.out')
        out_txt = out_txt.replace('\\', '/')
        sixsDir = os.path.dirname(ZY3.SIXS_EXE).replace('\\', '/')
        cmdStr1 = 'cd ' + sixsDir
        cmdStr2 = '6s.exe<in.txt>log'
        os.system(cmdStr1 + ' && ' + cmdStr2)
        time.sleep(1)
        with open(out_txt, 'r') as (f):
            for line in f.readlines():
                line = line.strip('\n')
                if 'coefficients xa xb xc' in line:     # TODO 这边的获取参数有点问题
                    coefAll = re.findall(r'[\.\d]+', line)
                    xa = float(coefAll[0])
                    xb = float(coefAll[1])
                    xc = float(coefAll[2])
                    # params = line.replace('*', '').split(':')[1].strip()
                    # xa = float(params.split('  ')[0])
                    # xb = float(params.split('  ')[1])
                    # xc = float(params.split('  ')[2])
        return xa, xb, xc

    def bandMath(self):
        """波段运算"""
        self.logObj.info("开始波段运算，处理信息如下...")
        self.logObj.info("卫星传感器类型：")
        self.logObj.info(self.satellite + ' ' + self.sensor)
        self.logObj.info("辐射定标参数：")
        self.logObj.info(self.radCorrectParam)
        self.logObj.info("大气校正参数：")
        self.logObj.info(self.atmCorrectParam)

        satSor = self.satellite + '_' + self.sensor
        tifName = self.basename + ZY3.FILE_SUFFIX[satSor] + '.tiff'
        tifPath = self.uncompressFile[tifName]['path']
        inDs = gdal.Open(tifPath)
        inWidth = inDs.RasterXSize
        inHeight = inDs.RasterYSize
        inBands = inDs.RasterCount
        driver = gdal.GetDriverByName('GTiff')
        self.noProjTifPath = os.path.join(self.tempDir, self.basename + '_noporj.tiff')
        outDs = driver.Create(self.noProjTifPath, inWidth, inHeight, inBands, gdal.GDT_UInt16)
        for i in range(4):
            bandI = inDs.GetRasterBand(i+1).ReadAsArray()
            bandTempI = bandI * self.radCorrectParam['gain'][i] + self.radCorrectParam['offset'][i]
            xa = self.atmCorrectParam['xa'][i]
            xb = self.atmCorrectParam['xb'][i]
            xc = self.atmCorrectParam['xc'][i]
            ref = (xa * bandTempI - xb) / (1 + xc * (xa * bandTempI - xb)) * 1000
            outDs.GetRasterBand(i + 1).WriteArray(ref)
        del outDs
        self.logObj.info("完成波段运算...")
        return True

    def project(self):
        """rpc坐标转换"""
        satSor = self.satellite + '_' + self.sensor
        rpcName = self.basename + ZY3.FILE_SUFFIX[satSor] + '.rpb'
        if rpcName not in self.uncompressFile.keys():
            self.logObj.error("未找到对应rpb文件！")
            return False
        rpcPath = self.uncompressFile[rpcName]['path']
        copyName = os.path.basename(self.noProjTifPath).replace('.tiff', '.rpb')
        self.rpcCopyPath = os.path.join(self.tempDir, copyName)
        shutil.copyfile(rpcPath, self.rpcCopyPath)
        # TODO 输出文件命名
        dt = datetime.datetime.strptime(self.centerTime, "%Y-%m-%d %H:%M:%S")
        issue = dt.strftime("%Y%m%d%H%M%S")
        outputName = '_'.join([self.satellite, self.sensor, '6', 'L2', issue, '000', '004']) + '.tif'
        self.outputPath = os.path.join(r'F:\zktq\data\process\luomahu', outputName)
        gdal.Warp(self.outputPath, self.noProjTifPath, rpc=True)
        self.logObj.info("地理校正成功...")
        return True

    def deleteTempFile(self):
        """删除临时文件"""
        try:
            # 1.解压缩文件夹
            shutil.rmtree(self.uncompressDir)
            # 2.noproj文件
            os.remove(self.noProjTifPath)
            os.remove(self.rpcCopyPath)
            self.logObj.info("删除临时文件成功")
            return True
        except Exception as e:
            self.logObj.error(e)
            return False


if __name__ == '__main__':

    inputDir = r'F:\zktq\data\original\luomahu\ZY'
    tempDir = r'C:\Users\Think\Desktop\temp'
    fileList = os.listdir(inputDir)
    for f in fileList:
        inputPath = os.path.join(inputDir, f)
        outputPath = 'None'

        gfObj = ZY3(inputPath, tempDir, outputPath)

        gfObj.doInit()

        # 1.解压文件
        gfObj.uncompress()

        # 2.辐射定标参数
        gfObj.radiometricCorrection()

        # 3.大气校正参数
        gfObj.atmosphericCorrection()

        # 4.波段运算
        gfObj.bandMath()

        # 5.rpc投影
        gfObj.project()

        # 6.删除临时文件
        gfObj.deleteTempFile()

    # inputPath = r'F:\zktq\data\original\taihu\ZY\ZY3_MUX_E120.0_N31.1_20190504_L1A0004317668.zip'
    # tempDir = r'C:\Users\Think\Desktop\temp'
    # outputPath = r'C:\Users\Think\Desktop\output\ZY3_MUX_E120.6_N31.5_20190509_L1A0004324603.tif'
    #
    # zyObj = ZY3(inputPath, tempDir, outputPath)
    #
    # zyObj.doInit()
    #
    # # 1.解压文件
    # zyObj.uncompress()
    #
    # # 2.辐射定标参数
    # zyObj.radiometricCorrection()
    #
    # # 3.大气校正参数
    # zyObj.atmosphericCorrection()
    #
    # # 4.波段运算
    # zyObj.bandMath()
    #
    # # 5.rpc投影
    # zyObj.project()
    #
    # # 6.删除临时文件
    # zyObj.deleteTempFile()
    #
    # print('Finish')
