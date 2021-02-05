# -*- coding: utf-8 -*-

"""
    调用MCTK处理MODIS250米数据
"""
import os
import sys
import time
import subprocess

import gdal
import numpy as np

"""
    IDL_RUNTIME_PATH: IDL虚拟机运行路径
    IDL_SAV_PATH: IDL封装sav文件路径
    HDF_TYPE: 输入数据类型 1:官网数据 2:星地通数据
"""

CONFIG = {
    'IDL_RUNTIME_PATH': 'C:/Program Files/Exelis/IDL83/bin/bin.x86_64/idlrt.exe',
    'IDL_SAV_PATH': 'C:/Users/Administrator/Desktop/jiangsu_water2_data/MODIS_L1B_PROCESS/MODIS_L1B_PROCESS.sav',
    'HDF_TYPE': 1
}


def processMain(inFile, outDir, outName):
    """
    @param inFile: 输入文件路径
    @param outDir: 输出文件夹路径
    @param outName: 输出文件名
    @return:
    """
    idlRtPath = CONFIG['IDL_RUNTIME_PATH']
    idlSavPath = CONFIG['IDL_SAV_PATH']
    idlRtPath = idlRtPath.replace('\\', '/')
    idlSavPath = idlSavPath.replace('\\', '/')
    inFile = inFile.replace('\\', '/')
    outDir = outDir.replace('\\', '/')
    outRootName = outputName.split('.')[0]
    if not outDir.endswith('/'):
        outDir += '/'
    cmdStr = '"%s" "%s" -args %s %s %s' % (idlRtPath, idlSavPath, inFile, outDir, outRootName)
    # ===========执行idl程序=============== #
    # p = subprocess.Popen(cmdStr, close_fds=True)
    # tBegin = time.time()
    # while True:
    #     if p.poll() is not None:
    #         break
    #     secondsDelay = time.time() - tBegin
    #     # 默认超时时间30分钟
    #     if secondsDelay > 60 * 30:
    #         p.kill()
    #         raise TimeoutError("Cmd Execute Out of Time!")
    #     time.sleep(5)
    # ==================================== #

    idlOutFile = os.path.join(outDir, outRootName + '_radiance_georef.dat')
    if not os.path.exists(idlOutFile):
        raise FileNotFoundError('Cannot Found IDL Out File.')

    # 将IDL输出的.dat文件处理为无符号整型.tif文件
    ds = gdal.Open(idlOutFile, gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    bands = ds.RasterCount
    proj = ds.GetProjection()
    trans = ds.GetGeoTransform()
    outTifPath = os.path.join(outDir, outName)
    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outTifPath, width, height, bands, gdal.GDT_UInt16)
    outDs.SetProjection(proj)
    outDs.SetGeoTransform(trans)
    for i in range(bands):
        bandArray = ds.GetRasterBand(i+1).ReadAsArray()
        nanLocation = bandArray == 65535
        bandArray = bandArray * 100
        bandArray = bandArray.astype(np.uint16)
        bandArray[nanLocation] = 65535
        outDs.GetRasterBand(i+1).WriteArray(bandArray)
    outDs = None
    print('Finish')


if __name__ == '__main__':
    inputFile = r'C:\Users\Administrator\Desktop\hdf\MYD02QKM.A2020247.0450.061.2020247154608.hdf'
    outputDir = r'C:\Users\Administrator\Desktop\hdf\MCTK_Output'
    outputName = r'test.tif'

    startTime = time.time()

    processMain(inputFile, outputDir, outputName)

    endTime = time.time()
    costTime = endTime - startTime
    print('Cost %s' % str(costTime))