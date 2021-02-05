# -*- coding: utf-8 -*-
"""tif文件缓冲区计算"""

import os
import gdal
import numpy as np
from GdalUtil import GdalUtil


def expand(tifPath, outTifPath):
    """向外扩一个像元"""
    # tifPath = r'C:\Users\Administrator\Desktop\depend\taihu_mask_utm[0].tif'
    # outTifPath = r'C:\Users\Administrator\Desktop\depend\taihu_mask_utm[1].tif'

    ds = gdal.Open(tifPath, gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    dataArray = ds.GetRasterBand(1).ReadAsArray()
    copyArray = np.copy(dataArray)

    # 向外缓冲1
    # 先找到边缘像元
    for i in range(width):
        for j in range(height):
            if dataArray[i][j] != 1:
                continue
            # 上下左右像元值
            pixel_1 = dataArray[i-1][j]
            pixel_2 = dataArray[i+1][j]
            pixel_3 = dataArray[i][j-1]
            pixel_4 = dataArray[i][j+1]
            if pixel_1 == 0 or pixel_2 == 0 or pixel_3 == 0 or pixel_4 == 0:
                # 边缘值
                copyArray[i-1][j] = 1
                copyArray[i+1][j] = 1
                copyArray[i][j-1] = 1
                copyArray[i][j+1] = 1

    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outTifPath, width, height, 1, gdal.GDT_Byte)
    outDs.SetGeoTransform(ds.GetGeoTransform())
    outDs.SetProjection(ds.GetProjection())
    outDs.GetRasterBand(1).WriteArray(copyArray)
    ds = None
    outDs = None
    print('Finish')


def reduce(tifPath, outTifPath):
    """向内缩一个像元"""
    # tifPath = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\NPP_VIIRS_375\taihu_mask_utm[-9].tif'
    # outTifPath = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\NPP_VIIRS_375\taihu_mask_utm[-10].tif'

    ds = gdal.Open(tifPath, gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    dataArray = ds.GetRasterBand(1).ReadAsArray()
    copyArray = np.copy(dataArray)

    # 向内缓冲1
    # 先找到边缘像元
    for i in range(width):
        for j in range(height):
            if dataArray[i][j] != 1:
                continue
            # 上下左右像元值
            pixel_1 = dataArray[i-1][j]
            pixel_2 = dataArray[i+1][j]
            pixel_3 = dataArray[i][j-1]
            pixel_4 = dataArray[i][j+1]
            if pixel_1 == 0 or pixel_2 == 0 or pixel_3 == 0 or pixel_4 == 0:
                # 是边缘值就设为0
                copyArray[i][j] = 0

    driver = gdal.GetDriverByName("GTiff")
    outDs = driver.Create(outTifPath, width, height, 1, gdal.GDT_Byte)
    outDs.SetGeoTransform(ds.GetGeoTransform())
    outDs.SetProjection(ds.GetProjection())
    outDs.GetRasterBand(1).WriteArray(copyArray)
    ds = None
    outDs = None
    print('Finish')


if __name__ == '__main__':

    # shp_path = r'C:\Users\Administrator\Desktop\jiangsu_water2_data\shp\taihu_admin.shp'
    # out_path = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\10\taihu_admin.tif'
    # out_bounds = (195203.762, 3418022.181, 282703.762, 3505522.181)
    # GdalUtil.shp_rasterize(shp_path, out_path, 10, 10, 'Id', out_bounds=out_bounds)
    #
    # shp_path = r'C:\Users\Administrator\Desktop\jiangsu_water2_data\shp\taihu_region.shp'
    # out_path = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\10\taihu_region.tif'
    # out_bounds = (195203.762, 3418022.181, 282703.762, 3505522.181)
    # GdalUtil.shp_rasterize(shp_path, out_path, 10, 10, 'Id', out_bounds=out_bounds)
    #
    # shp_path = r'C:\Users\Administrator\Desktop\jiangsu_water2_data\shp\taihu.shp'
    # out_path = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\10\taihu_mask_utm[0].tif'
    # out_bounds = (195203.762, 3418022.181, 282703.762, 3505522.181)
    # GdalUtil.shp_rasterize(shp_path, out_path, 10, 10, 'Id', out_bounds=out_bounds, nodataValue=0)

    # rootDir = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\10'
    # for i in range(10):
    #     inFileName = 'taihu_mask_utm[%s].tif' % i
    #     outFileName = 'taihu_mask_utm[%s].tif' % (i+1)
    #     inFilePath = os.path.join(rootDir, inFileName)
    #     outFilePath = os.path.join(rootDir, outFileName)
    #     reduce(inFilePath, outFilePath)
    #     print('Finish: %s' % outFileName)
    #
    # for i in range(10):
    #     inFileName = 'taihu_mask_utm[%s].tif' % i
    #     outFileName = 'taihu_mask_utm[%s].tif' % -(i+1)
    #     inFilePath = os.path.join(rootDir, inFileName)
    #     outFilePath = os.path.join(rootDir, outFileName)
    #     expand(inFilePath, outFilePath)
    #     print('Finish: %s' % outFileName)

    shp_path = r'E:\Data\output\L8-S2\roi.shp'
    out_path = r'E:\Data\output\L8-S2\roi.tif'
    out_bounds = (275910, 3470420, 295090, 3487160)
    GdalUtil.shp_rasterize(shp_path, out_path, 10, 10, 'Id', out_bounds=out_bounds)
