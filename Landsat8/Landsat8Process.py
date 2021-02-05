# -*- coding: utf-8 -*-

import os
import tarfile
import xml.dom.minidom

import gdal
import numpy as np


def parseXml(xmlPath):
    """解析XML文件并返回相关信息"""

    xmlInfo = {}  # 配置文件解析信息
    dom = xml.dom.minidom.parse(xmlPath)
    for eachNode in dom.getElementsByTagName('PRODUCT_CONTENTS')[0].childNodes:
        # 非文本节点跳过
        if eachNode.nodeType != 1:
            continue
        if eachNode.nodeName == 'LANDSAT_PRODUCT_ID':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
    for eachNode in dom.getElementsByTagName('IMAGE_ATTRIBUTES')[0].childNodes:
        if eachNode.nodeType != 1:
            continue
        if eachNode.nodeName == 'DATE_ACQUIRED':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'SCENE_CENTER_TIME':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'CLOUD_COVER':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'SUN_AZIMUTH':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'SUN_ELEVATION':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
    for eachNode in dom.getElementsByTagName('LEVEL1_RADIOMETRIC_RESCALING')[0].childNodes:
        if eachNode.nodeType != 1:
            continue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_1':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_2':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_3':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_4':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_5':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_6':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_MULT_BAND_7':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_1':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_2':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_3':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_4':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_5':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_6':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue
        if eachNode.nodeName == 'RADIANCE_ADD_BAND_7':
            xmlInfo[eachNode.nodeName] = eachNode.childNodes[0].nodeValue

    return xmlInfo


def getProcessFile(dirPath, bandList):
    """获取需要处理的文件路径"""
    # 初始化波段对应文件路径信息字典
    fileDict = {}
    for each in bandList:
        fileDict.setdefault(each)

    for fileName in os.listdir(dirPath):
        bandIndex = fileName.split('_')[-1].split('.')[0]
        if bandIndex in fileDict.keys():
            fileDict[bandIndex] = os.path.join(dirPath, fileName)
    if None in fileDict.values():
        return None
    return fileDict


def main(inFile, tempDir, outPath):
    # 解压文件
    basename = os.path.basename(inFile).split('.')[0]
    uncompressDir = os.path.join(tempDir, basename)
    t = tarfile.open(inFile)
    t.extractall(path=uncompressDir)

    # 1.读取配置文件
    mltFile = os.path.join(uncompressDir, basename + '_MTL.xml')
    if not os.path.exists(mltFile):
        print('Cannot Find MTL File.')
    mtlInfo = parseXml(mltFile)

    # 2.获取需要处理的波段文件
    bandList = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']  # 待处理波段
    bandFilePath = getProcessFile(uncompressDir, bandList)

    # 3.获取输出文件基本信息
    ds = gdal.Open(list(bandFilePath.values())[0], gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    bands = len(bandList)
    proj = ds.GetProjection()
    geoTrans = ds.GetGeoTransform()
    ds = None

    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outPath, width, height, bands, gdal.GDT_Float32)
    outDs.SetGeoTransform(geoTrans)
    outDs.SetProjection(proj)
    for i in range(len(bandList)):
        # print(i + 1)
        print(bandFilePath[bandList[i]])
        ds = gdal.Open(bandFilePath[bandList[i]], gdal.GA_ReadOnly)
        bandArray = ds.GetRasterBand(1).ReadAsArray()
        ds = None
        gain = eval(mtlInfo['RADIANCE_MULT_BAND_' + str(i + 1)])
        offset = eval(mtlInfo['RADIANCE_ADD_BAND_' + str(i + 1)])
        print(gain)
        print(offset)
        radianceArray = bandArray * gain + offset
        outDs.GetRasterBand(i + 1).WriteArray(radianceArray)
    outDs = None
    print('Finish.')


if __name__ == '__main__':

    inTarFile = r'E:\Data\input\LC08_L1TP_119038_20190226_20200829_02_T1.tar'
    tempDir = r'E:\Data\temp'
    outFile = r'E:\Data\output\landsat.tif'

    main(inTarFile, tempDir, outFile)