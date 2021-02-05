# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/13 15:19

"""
    多波段栅格数据像元值转为0-255范围
"""

import os

import gdal
import numpy as np


PYTHON_PATH = 'D:/Miniconda3/envs/jiangsu_water_demo_model/python'
GDAL2TILES_PATH = 'D:/Miniconda3/envs/jiangsu_water_demo_model/Scripts/gdal2tiles.py'


def process(inputFile, outputFile, bandComb, nanValue):
    """
    输入文件数据类型转化，并处理为RGB组合形式
    @param inputFile: str: 输入文件路径
    @param outputFile: str: 输出文件路径
    @param bandComb: tuple: 波段组合形式(R, G, B)
    @param nanValue: float: 栅格中无效值大小
    @return:
    """
    inDs = gdal.Open(inputFile)
    bands = inDs.RasterCount
    if len(bandComb) != 3 or max(bandComb) > bands:
        print("波段组合设置异常！")
        del inDs
        return None
    width = inDs.RasterXSize
    height = inDs.RasterYSize
    proj = inDs.GetProjection()
    trans = inDs.GetGeoTransform()

    # 先遍历一遍所有波段，把无效值位置寻找出来
    bandNanCount = np.zeros((height, width), dtype=np.uint8)  # 像元三个波段都等于无效值才设置透明
    for i in range(len(bandComb)):
        bandArray = inDs.GetRasterBand(bandComb[i]).ReadAsArray()
        bandNanCount[bandArray == nanValue] += 1

    outDriver = gdal.GetDriverByName("GTiff")
    outDs = outDriver.Create(outputFile, width, height, 4, gdal.GDT_Byte)
    outDs.SetProjection(proj)
    outDs.SetGeoTransform(trans)

    # 依次进行RGB波段数值转换
    for i in range(len(bandComb)):
        bandArray = inDs.GetRasterBand(bandComb[i]).ReadAsArray()
        bandMin = np.nanmin(bandArray[bandNanCount == 0])  # 去除无效值后最小值
        bandMax = np.nanmax(bandArray[bandNanCount == 0])  # 去除无效值后最大值
        # 将DN值归一化到0-255
        # 转换公式：y = (x - array_min)/(array_max - array_min) * (stretch_max - stretch_min) + stretch_min
        bandArrayByte = (bandArray - bandMin) / (bandMax - bandMin) * (255 - 0) + 0
        bandArrayByte[bandArrayByte < 0] = 0
        bandArrayByte[bandArrayByte > 255] = 255
        bandArrayByte = bandArrayByte.astype(np.uint8)
        outDs.GetRasterBand(i+1).WriteArray(bandArrayByte)

    # 写入Alpha波段
    alphaArray = np.ones((height, width), dtype=np.uint8) * 255
    alphaArray[bandNanCount == 3] = 0
    outDs.GetRasterBand(4).WriteArray(alphaArray)
    outDs = None


def LinearPercent(inputFile, outputFile, percent):
    """
    百分之X线性拉伸
    将直方图累积在X%和100-X%之间的像元值拉伸，取直方图累积在X%处对应的光谱值为MinValue，100-X%处对应的光谱值为MaxValue，
    如果像元值大于MinValue且小于MaxValue，则将其拉伸至0-255；
    如果像元值小于MinValue，赋值0；如果像元值大于MaxValue，赋值255。

    @param inputFile: 输入RGBA图像      TODO 支不支持3波段？
    @param outputFile: 输出拉伸结果
    @param percent: 拉伸百分比
    @return:
    """
    inDs = gdal.Open(inputFile)
    width = inDs.RasterXSize
    height = inDs.RasterYSize
    proj = inDs.GetProjection()
    trans = inDs.GetGeoTransform()

    alphaArray = inDs.GetRasterBand(4).ReadAsArray()

    outDriver = gdal.GetDriverByName("GTiff")
    outDs = outDriver.Create(outputFile, width, height, 4, gdal.GDT_Byte)
    outDs.SetProjection(proj)
    outDs.SetGeoTransform(trans)
    # 依次进行RGB波段数值转换
    for i in range(3):
        bandArray = inDs.GetRasterBand(i+1).ReadAsArray()
        bandMin = np.percentile(bandArray[alphaArray == 255], percent)
        bandMax = np.percentile(bandArray[alphaArray == 255], 100-percent)
        bandArray[bandArray < bandMin] = bandMin
        bandArray[bandArray > bandMax] = bandMax
        # 转换公式：y = (x - array_min)/(array_max - array_min) * (stretch_max - stretch_min) + stretch_min
        bandArrayByte = (bandArray - bandMin) / (bandMax - bandMin) * (255 - 0) + 0
        bandArrayByte[bandArrayByte < 0] = 0
        bandArrayByte[bandArrayByte > 255] = 255
        bandArrayByte = bandArrayByte.astype(np.uint8)
        outDs.GetRasterBand(i + 1).WriteArray(bandArrayByte)

    # 写入Alpha波段
    outDs.GetRasterBand(4).WriteArray(alphaArray)
    outDs = None


if __name__ == '__main__':

    # 输入数据
    inputTif = r'C:\Users\Administrator\Desktop\AQ.tif'
    # 临时文件夹
    tempDir = r'C:\Users\Administrator\Desktop\temp'
    nanV = 65535

    basename = os.path.basename(inputTif).replace('.tif', '')
    processTif = os.path.join(tempDir, basename + '_byte.tif')

    bandCombine = (1, 2, 1)
    process(inputTif, processTif, bandCombine, nanV)

    enhanceTif = os.path.join(tempDir, basename + '_enhance.tif')
    percentValue = 2
    LinearPercent(processTif, enhanceTif, percentValue)

    # 切片假彩色图
    tileDir = r'C:\Users\Administrator\Desktop\model\tile-server'
    falseColorDir = os.path.join(tileDir, basename + '_falseColor')

    # 1.执行器
    pythonPath = PYTHON_PATH
    # 2.切片脚本路径
    scriptPath = GDAL2TILES_PATH
    # 3.切片等级
    zoomLevel = '8-13'

    cmd = '%s %s -z %s -w all %s %s' % (pythonPath, scriptPath, zoomLevel, enhanceTif, falseColorDir)
    os.system(cmd)

    print('Finish')