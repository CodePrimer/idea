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


class GF(object):

    # GF辐射定标参数文件
    RAD_CORRECT_PARAM = os.path.join(os.path.dirname(__file__), 'RadCorrectParam_GF.json')

    # 6s大气校正exe路径
    SIXS_EXE = os.path.join(os.path.dirname(__file__), '6S_IDL_NOBRDF', 'main.exe')

    # 波长范围
    WAVE_RANGE = [[0.45, 0.52],
                  [0.52, 0.59],
                  [0.63, 0.69],
                  [0.77, 0.89]]

    # 解压缩文件路径
    FILE_PATH = 'FILE_PATH'

    # 解压缩文件传感器类型
    FILE_SENSOR = 'FILE_SENSOR'

    # 解压缩文件后缀
    FILE_EXT = 'FILE_EXT'

    def __init__(self, inputPath, tempDir, outputDir, logPath=None):
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

        # 中间数据
        self.uncompressDir = None           # 解压文件夹根目录
        self.uncompressFileList = []        # list:解压后文件名
        self.uncompressFileClassify = {}    # dict:解压后按照传感器文件清单
        self.radCorrectParam = {}           # dict:辐射定标参数 {'gain':[], 'offset':[]}
        self.atmCorrectParam = {}           # dict:6s大气校正参数 {'xa': [], 'xb': [], 'xc': []}
        # self.noProjTifPath = None           # 中间生成的未投影文件路径
        # self.rpcCopyPath = None             # 复制rpb文件路径
        self.centerTime = None              # 数据获取时间
        # 输出信息
        self.outputDir = outputDir         # str:输出文件路径

    def doInit(self):
        """
        类对象初始化操作
        1.初始化Log文件  DELETE
        2.有效性检查
            2.1 输入文件是否存在
            2.2 输入文件名正则是否符合规则
            2.3 创建临时文件夹
        3.获取文件基本信息
        """

        # 2.有效性检查
        # 2.1 输入文件是否存在
        if not os.path.exists(self.inputPath):
            print("输入文件不存在！")
            return False
        # 2.2 输入文件名正则是否符合规则 TODO 暂时只做下划线分割长度判断
        if os.path.isfile(self.inputPath):
            if self.inputPath.endswith('.zip'):
                self.basename = os.path.basename(self.inputPath).replace('.zip', '')
                self.ext = '.zip'
            elif self.inputPath.endswith('.tar.gz'):
                self.basename = os.path.basename(self.inputPath).replace('.tar.gz', '')
                self.ext = '.tar.gz'
            else:
                print("未知的文件格式！")
                return False
        elif os.path.isdir(self.inputPath):
            self.basename = os.path.basename(self.inputPath)
        else:
            return False
        filenameInfo = self.basename.split('_')
        if len(filenameInfo) != 6:
            print("文件名格式错误！")
            return False
        # 2.3 创建临时文件夹
        try:
            if not os.path.isdir(self.tempDir):
                pass
                # os.makedirs(self.tempDir)
        except Exception as e:
            print.error("创建临时文件失败！")
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

    def classifyUncompressFile(self):
        for each in self.uncompressFileList:
            filePath = each
            fileName = os.path.basename(each)
            fileExt = os.path.splitext(fileName)[1]

            tmpValue = fileName.replace(self.basename, '').replace(os.path.splitext(fileName)[1], '')
            if '-' in tmpValue and len(tmpValue.split('_')) == 1:
                fileSensor = tmpValue.replace('-', '')
            else:
                continue
            if fileSensor not in self.uncompressFileClassify.keys():
                self.uncompressFileClassify[fileSensor] = {'.xml': '', '.rpb': '', '.tiff': ''}
            if fileExt == '.xml':
                self.uncompressFileClassify[fileSensor]['.xml'] = filePath
            elif fileExt == '.rpb':
                self.uncompressFileClassify[fileSensor]['.rpb'] = filePath
            elif fileExt == '.tiff':
                self.uncompressFileClassify[fileSensor]['.tiff'] = filePath
            else:
                continue

    def classifyFile(self):
        fileList = os.listdir(self.inputPath)
        for f in fileList:
            filePath = os.path.join(self.inputPath, f)
            fileName = f
            fileExt = os.path.splitext(fileName)[1]

            tmpValue = fileName.replace(self.basename, '').replace(os.path.splitext(fileName)[1], '')
            if '-' in tmpValue and len(tmpValue.split('_')) == 1:
                fileSensor = tmpValue.replace('-', '')
            else:
                continue
            if fileSensor not in self.uncompressFileClassify.keys():
                self.uncompressFileClassify[fileSensor] = {'.xml': '', '.rpb': '', '.tiff': ''}
            if fileExt == '.xml':
                self.uncompressFileClassify[fileSensor]['.xml'] = filePath
            elif fileExt == '.rpb':
                self.uncompressFileClassify[fileSensor]['.rpb'] = filePath
            elif fileExt == '.tiff':
                self.uncompressFileClassify[fileSensor]['.tiff'] = filePath
            else:
                continue

    def uncompress(self):
        """解压缩文件"""
        self.uncompressDir = os.path.join(self.tempDir, self.basename)
        if zipfile.is_zipfile(self.inputPath):
            print("压缩文件格式为zip，开始解压...")
            zFile = zipfile.ZipFile(self.inputPath, 'r')
            for f in zFile.namelist():
                zFile.extract(f, self.uncompressDir)
                self.uncompressFileList.append(os.path.join(self.uncompressDir, f))

        elif tarfile.is_tarfile(self.inputPath):
            print("压缩文件格式为tar，开始解压...")
            tFile = tarfile.open(self.inputPath)
            for f in tFile.getnames():
                tFile.extract(f, self.uncompressDir)
                self.uncompressFileList.append(os.path.join(self.uncompressDir, f))

        elif rarfile.is_rarfile(self.inputPath):
            print("压缩文件格式为rar，开始解压...")
            rFile = rarfile.RarFile(self.inputPath, mode='r')
            for f in rFile.namelist():
                rFile.extract(f, self.uncompressDir)
                self.uncompressFileList.append(os.path.join(self.uncompressDir, f))
        else:
            print("无法识别的压缩文件格式！")
            return False

        self.classifyUncompressFile()   # 整理解压缩文件

        print("解压缩文件成功.")

    def radiometricCorrection(self):
        """辐射定标，为了减少IO这里先获取辐射定标参数"""
        radJsonFile = GF.RAD_CORRECT_PARAM
        jsonData = json.load(open(radJsonFile))
        if self.year in jsonData[self.satellite][self.sensor].keys():
            param = jsonData[self.satellite][self.sensor][self.year]
        else:
            param = jsonData[self.satellite][self.sensor]['latest']
        self.radCorrectParam = param
        print("获取辐射定标参数成功...")

    def atmosphericCorrection(self):
        """获取大气校正参数并进行计算"""
        xmlPath = ''
        for key in self.uncompressFileClassify.keys():
            if key in ['MUX', 'MUX1', 'MUX2', 'MSS1', 'MSS2']:
                xmlPath = self.uncompressFileClassify[key]['.xml']
                break
        if xmlPath == '':
            print("未找到对应xml文件！")
            return False

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
                                            centerLon, centerLat, GF.WAVE_RANGE[i])
            self.atmCorrectParam['xa'].append(xa)
            self.atmCorrectParam['xb'].append(xb)
            self.atmCorrectParam['xc'].append(xc)
        print("获取6S大气校正参数成功...")

    def getSixsParams(self, mm, dd, SolarZenith, SolarAzimuth, SatelliteZenith, SatelliteAzimuth, lon, lat, wave):
        """运行6s模型"""
        igeom = '0\n'
        asol = str(90 - SolarZenith) + '\n'
        phio = str(SolarAzimuth) + '\n'
        if self.satellite in ['GF1B', 'GF1C', 'GF1D']:
            avis = str(SatelliteZenith) + '\n'
        else:
            avis = str(90 - SatelliteZenith) + '\n'
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
        in_txt = os.path.join(os.path.dirname(GF.SIXS_EXE), 'in.txt')
        in_txt = in_txt.replace('\\', '/')
        with open(in_txt, 'w') as (f):
            f.writelines(file_content)
        out_txt = os.path.join(os.path.dirname(GF.SIXS_EXE), 'sixs.out')
        out_txt = out_txt.replace('\\', '/')
        sixsDir = os.path.dirname(GF.SIXS_EXE).replace('\\', '/')
        cmdStr1 = 'cd ' + sixsDir
        cmdStr2 = 'main.exe<in.txt>sixs.out'
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
        print("开始波段运算")

        for each in self.uncompressFileClassify.keys():
            if each not in ['MUX', 'MUX1', 'MUX2', 'MSS1', 'MSS2']:
                continue
            else:
                tifPath = self.uncompressFileClassify[each]['.tiff']
                inDs = gdal.Open(tifPath)
                inWidth = inDs.RasterXSize
                inHeight = inDs.RasterYSize
                inBands = inDs.RasterCount
                driver = gdal.GetDriverByName('GTiff')
                self.noProjTifPath = os.path.join(self.outputDir, os.path.basename(tifPath))
                outDs = driver.Create(self.noProjTifPath, inWidth, inHeight, inBands, gdal.GDT_UInt16)
                for i in range(4):
                    bandI = inDs.GetRasterBand(i+1).ReadAsArray()
                    bandTempI = bandI * self.radCorrectParam['gain'][i] + self.radCorrectParam['offset'][i]
                    xa = self.atmCorrectParam['xa'][i]
                    xb = self.atmCorrectParam['xb'][i]
                    xc = self.atmCorrectParam['xc'][i]
                    ref = (xa * bandTempI - xb) / (1 + xc * (xa * bandTempI - xb)) * 10000
                    outDs.GetRasterBand(i + 1).WriteArray(ref)
                outDs = None
                print("完成波段运算...")

                # 拷贝文件
                rpcPath = self.uncompressFileClassify[each]['.rpb']
                rpcCopyPath = os.path.join(self.outputDir, os.path.basename(rpcPath))
                shutil.copyfile(rpcPath, rpcCopyPath)

                xmlPath = self.uncompressFileClassify[each]['.xml']
                xmlCopyPath = os.path.join(self.outputDir, os.path.basename(xmlPath))
                shutil.copyfile(xmlPath, xmlCopyPath)
                print("完成rpc和xml拷贝...")

        return True

    def deleteTempFile(self):
        """删除临时文件"""
        try:
            if os.path.exists(self.tempDir):
                shutil.rmtree(self.tempDir)
                print("删除临时文件成功")
            return True
        except Exception as e:
            return False

    @staticmethod
    def main(inputPath, outputDir):

        tempDir = os.path.join(os.path.dirname(inputPath), '_temp' + str(int(time.time() * 1000)))
        if not os.path.exists(tempDir):
            pass
            # os.makedirs(tempDir)

        gfObj = GF(inputPath, tempDir, outputDir)

        gfObj.doInit()

        # 1.解压文件
        if os.path.isdir(gfObj.inputPath):
            gfObj.classifyFile()
        else:
            gfObj.uncompress()
        # 2.辐射定标参数
        gfObj.radiometricCorrection()

        # 3.大气校正参数
        gfObj.atmosphericCorrection()

        # 4.波段运算
        gfObj.bandMath()

        # 6.删除临时文件
        gfObj.deleteTempFile()


if __name__ == '__main__':

    inputPath = r'E:\Data\GF\GF1B_PMS_E109.9_N20.7_20191211_L1A1227738615'
    # tempDir = r'C:\Users\Administrator\Desktop\temp'
    outputDir = r'C:\Users\Administrator\Desktop\output\GF1B_PMS_E109.9_N20.7_20191211_L1A1227738615'
    GF.main(inputPath, outputDir)