# -*- coding: utf-8  -*-
# -*- author: htht -*-

import os
import gdal
import numpy as np


class GeoTiffFile(object):
    """
    TIF文件类
    实现：1.读取TIF。2.新建TIF。3.修改TIF
    """

    # gdal.GDT
    BYTE = gdal.GDT_Byte            # [0, 255] - 1Byte
    INT16 = gdal.GDT_Int16          # [-32768, 32767] - 2Byte
    INT32 = gdal.GDT_Int32          # [-2147483648, 2147483647] - 4Byte
    UINT16 = gdal.GDT_UInt16        # [0, 65535] - 2Byte
    UINT32 = gdal.GDT_UInt32        # [0, 4294967295] - 4Byte
    FLOAT32 = gdal.GDT_Float32      # [-3.4e38, 3.4e38] - 4Byte
    FLOAT64 = gdal.GDT_Float64      # [1.7E-308, 1.7E+308] - 8Byte

    def __init__(self, tifPath):
        self.__tifPath = tifPath    # str:文件路径
        self.__ds = None            # osgeo.gdal.Dataset:数据集
        self.__width = None         # int:栅格宽度
        self.__height = None        # int:栅格高度
        self.__bands = None         # int:栅格波段数
        self.__proj = None          # str:投影信息
        self.__geoTrans = None      # tuple:仿射矩阵[左上角x,东西向分辨率,旋转,左上角y,旋转,南北向分辨率]
        self.__xRes = None          # float:x方向分辨率
        self.__yRes = None          # float:y方向分辨率
        self.__dtype = None         # numpy.dtype:数据类型
        self.__data = None          # numpy.ndarray:数据数组

    def readTif(self):
        """加载TIF信息"""
        ds = gdal.Open(self.__tifPath, gdal.GA_ReadOnly)
        if ds is None:
            print("Cannot Open TifFile: %s" % self.__tifPath)
            return
        self.__ds = ds
        self.__width = ds.RasterXSize
        self.__height = ds.RasterYSize
        self.__bands = ds.RasterCount
        self.__proj = ds.GetProjection()
        self.__geoTrans = ds.GetGeoTransform()
        self.__xRes = abs(ds.GetGeoTransform()[1])
        self.__yRes = abs(ds.GetGeoTransform()[5])
        # TODO 是否有其他方法获取数据类型
        self.__dtype = ds.GetRasterBand(1).ReadAsArray(0, 0, 1, 1).dtype

    def getDs(self):
        """获取TIF的dataset对象"""
        return self.__ds

    def getGeoTrans(self):
        """获取TIF的仿射矩阵"""
        return self.__geoTrans

    def getXRes(self):
        """获取TIF的x向分辨率"""
        return self.__xRes

    def getYRes(self):
        """获取TIF的y向分辨率"""
        return self.__yRes

    def getProj(self):
        """获取TIF的投影信息"""
        return self.__proj

    def getBandData(self, bandIndex):
        """
        获取TIF某波段的数据
        @param bandIndex: 波段索引，从0开始
        @return: numpy.ndarray
        """
        try:
            dt = self.__ds.GetRasterBand(bandIndex+1)
            return dt.ReadAsArray()
        except Exception as e:
            print(e)
            return None

    def getGeoExtent(self):
        """
        获取TIF经纬度范围
        @return: 字典 {"xMin": lonMin, "xMax": lonMax, "yMin": latMin, "yMax": latMax}
        """
        leftTopX = self.__geoTrans[0]
        leftTopY = self.__geoTrans[3]
        rightDownX = leftTopX + self.__geoTrans[1] * (self.__width - 1)
        rightDownY = leftTopY + self.__geoTrans[5] * (self.__height - 1)
        xMin = min([leftTopX, rightDownX])
        xMax = max([leftTopX, rightDownX])
        yMin = min([leftTopY, rightDownY])
        yMax = max([leftTopY, rightDownY])
        extent = {"xMin": xMin, "xMax": xMax, "yMin": yMin, "yMax": yMax}
        return extent

    def getWidth(self):
        """获取TIF的宽度"""
        return self.__width

    def getHeight(self):
        """获取TIF的高度"""
        return self.__height

    def getBands(self):
        """获取TIF的波段数"""
        return self.__bands

    def getDtype(self):
        """获取TIF的数据类型"""
        return self.__dtype

    def setDims(self, width, height, band):
        """设置TIF的宽度、高度、波段数"""
        self.__width = width
        self.__height = height
        self.__bands = band

    def setProj(self, proj):
        """设置TIF的投影信息"""
        self.__proj = proj

    def setGeoTrans(self, geoTrans):
        """设置TIF的仿射矩阵"""
        self.__geoTrans = geoTrans

    def setData(self, ndarray):
        """
        设置TIF的数据数组
        @param ndarray: numpy数组
        """
        if len(ndarray.shape) > 3 or len(ndarray.shape) == 1:
            return
        if len(ndarray.shape) == 2:
            ndarray = np.array([ndarray])
        self.__data = ndarray

    def writeTif(self):
        """输出TIF文件"""
        driver = gdal.GetDriverByName("GTiff")

        # numpy->GDAL数据类型对应表
        dtypeDict = {"uint8": GeoTiffFile.BYTE,
                     "int16": GeoTiffFile.INT16,
                     "int32": GeoTiffFile.INT32,
                     "uint16": GeoTiffFile.UINT16,
                     "uint32": GeoTiffFile.UINT32,
                     "float32": GeoTiffFile.FLOAT32,
                     "float64": GeoTiffFile.FLOAT64
                     }

        ds = driver.Create(self.__tifPath, self.__width, self.__height, self.__bands, dtypeDict[self.__data.dtype.name])
        ds.SetGeoTransform(self.__geoTrans)
        ds.SetProjection(self.__proj)
        for i in range(self.__bands):
            ds.GetRasterBand(i+1).WriteArray(self.__data[i])
        del ds


if __name__ == "__main__":

    # 读取TIF 写出TIF
    tifPath = r"C:\Users\Think\Desktop\ldf\FY3D_MERSI_WHOLE_GLL_L1_20190315_1519_1000M.ldf"
    tifObj = GeoTiffFile(tifPath)
    tifObj.readTif()

    bandR = tifObj.getBandData(3)
    bandIR = tifObj.getBandData(4)
    ndvi = (bandIR * 1.0 - bandR)/(bandIR + bandR)

    ds = tifObj.getDs()
    data1 = ds.ReadAsArray()

    outPath = r"C:\Users\Think\Desktop\test\fy3d.tif"

    outTifObj = GeoTiffFile(outPath)
    outTifObj.setDims(tifObj.getWidth(), tifObj.getHeight(), 1)
    outTifObj.setProj(tifObj.getProj())
    outTifObj.setGeoTrans(tifObj.getGeoTrans())
    outTifObj.setData(ndvi)
    outTifObj.writeTif()

    print("finish")
