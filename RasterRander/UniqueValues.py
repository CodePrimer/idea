# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/15 11:52

"""
    单波段栅格进行唯一值渲染。将输入的单波段数据按照颜色表输出为彩色图像。
    1.支持输出为带地理坐标的TIF格式，支持Alpha波段
    2.支持输出为不带地理坐标的图片格式(.png/.jpg)   # TODO 尚未实现
    3.支持设置背景值颜色/支持设置透明值颜色(二者选一)
    4.

"""

import os

import gdal
import numpy as np

# 固定常量
PYTHON_PATH = 'D:/Miniconda3/envs/jiangsu_water_demo_model/python'
GDAL2TILES_PATH = 'D:/Miniconda3/envs/jiangsu_water_demo_model/Scripts/gdal2tiles.py'


def main(inputFile, colorTable, outType='MEM', outputFile='', isAlpha=False, bgValue=(255, 255, 255)):
    """

    @param inputFile: str: 输入的单波段栅格文件路径
    @param colorTable: dict: 分级渲染颜色表  {value: (R, G, B)}
    @param outType: str: 输出数据类型:
                            'MEM': 将结果以numpy数组形式返回
                            'TIF': 将结果保存为GeoTIFF文件，并保留地理信息，可选透明波段
                            'PNG': 将结果保存为.png格式文件，可选透明波段
                            'JPG': 将结果保存为.jpg格式文件
    @param outputFile: str: 文件输出路径，若outType不是MEM，则必须填写本项
    @param isAlpha: bool: 是否带透明图层，默认无透明。未出现在分级渲染颜色表中的value会被设置透明。支持outType为MEM、TIF、PNG
    @param bgValue: tuple: 背景值RGB颜色，默认背景为白色。未出现在分级渲染颜色表中的value会设置为背景值。
    @return: numpy.array: outType为MEM时返回处理后数组。
    """
    # TODO 检查输入参数

    # 读取输入
    inDs = gdal.Open(inputFile)
    width = inDs.RasterXSize
    height = inDs.RasterYSize
    array = inDs.GetRasterBand(1).ReadAsArray()  # 读取输入的单通道数组

    rgbaArray = np.zeros((height, width, 4), dtype=np.uint8)  # 创建空的rgba数组
    # 依次循环颜色表进行像元颜色填充
    for each in colorTable.keys():
        rgbaArray[:, :, 0][array == each] = colorTable[each][0]
        rgbaArray[:, :, 1][array == each] = colorTable[each][1]
        rgbaArray[:, :, 2][array == each] = colorTable[each][2]
        rgbaArray[:, :, 3][array == each] += 1  # 将颜色表中出现过的数值像元值+1，最终0值像元为透明位置或背景色位置

    # 填充背景色
    rgbaArray[:, :, 0][rgbaArray[:, :, 3] == 0] = bgValue[0]
    rgbaArray[:, :, 1][rgbaArray[:, :, 3] == 0] = bgValue[1]
    rgbaArray[:, :, 2][rgbaArray[:, :, 3] == 0] = bgValue[2]
    # 填充透明
    rgbaArray[:, :, 3][rgbaArray[:, :, 3] != 0] = 255  # 有值区域透明设为255（不透明）

    if not isAlpha:     # 不要透明图层
        resultArray = rgbaArray[:, :, 0:3]
    else:               # 要透明图层
        resultArray = rgbaArray

    if outType == 'MEM':
        return resultArray
    elif outType == 'TIF':
        proj = inDs.GetProjection()
        trans = inDs.GetGeoTransform()
        outDriver = gdal.GetDriverByName("GTiff")        # 写出GeoTIFF结果
        outDs = outDriver.Create(outputFile, width, height, resultArray.shape[2], gdal.GDT_Byte)
        outDs.SetProjection(proj)
        outDs.SetGeoTransform(trans)
        for i in range(resultArray.shape[2]):
            outDs.GetRasterBand(i + 1).WriteArray(rgbaArray[:, :, i])
        outDs = None
    else:   # TODO 未完成jpg和png
        pass


if __name__ == '__main__':

    inputFile = r'G:\zktq\水色异常\20200503水色分级\shuisefenji4.tif'
    outputFile = r'C:\Users\Think\Desktop\output\shuisefenji4.tif'
    # colorTable = {0: (255, 0, 0)}
    # colorTable = {1: (91, 241, 136),
    #               2: (252, 153, 5)}       # 唯一值渲染颜色表
    # colorTable = {0: (8, 243, 70),
    #               1: (2, 255, 255)}
    colorTable = {1: (155, 178, 255),
                  2: (163, 255, 155),
                  3: (56, 168, 0),
                  4: (168, 168, 0),
                  5: (255, 170, 0),
                  6: (255, 0, 0)}

    main(inputFile, colorTable, outType='TIF', outputFile=outputFile, bgValue=(0, 0, 0), isAlpha=True)

    tileOutDir = r'C:\Users\Think\Desktop\model\tile-server\shuisefenji4'
    zoom = '8-13'
    cmd = '%s %s -z %s -w all %s %s' % (PYTHON_PATH, GDAL2TILES_PATH, zoom, outputFile, tileOutDir)
    os.system(cmd)