# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-


import os
from osgeo import gdal
from osgeo import ogr
import pandas as pd


class ShapeFile(object):

    def __init__(self, shpPath):
        self.__shpPath = shpPath    # str:文件路径
        self.__ds = None            # unknown:数据集
        self.__layer = None         # unknown:图层集
        self.__extent = None        # list:shp的空间范围(min_x,max_x,min_y,max_y)
        self.__fieldInfo = {}       # dict:属性表字段信息
        self.__fieldName = []       # list:属性表名称
        self.__featureCount = None  # int:记录条数
        self.__attrTable = None     # pandas.DataFrame:属性表数据

    def readShp(self):
        """
        打开shp文件并获取shp基本信息
        :return:
        """
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
        gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 为了使属性表字段支持中文，请添加
        ogr.RegisterAll()  # 注册所有的驱动
        ds = ogr.Open(self.__shpPath, gdal.GA_ReadOnly)
        if ds is None:
            print(u"无法打开指定shp文件: %s" % self.__shpPath)
            return

        self.__ds = ds
        self.__layer = ds.GetLayer(0)
        self.__extent = self.__layer.GetExtent()

        self.__fieldInfo = self.__getFieldInfo()
        self.__fieldName = self.__getFieldName()
        self.__featureCount = self.__layer.GetFeatureCount()
        self.__attrTable = self.__getAttrTable()

        # ds.Destroy()    # 析构 TODO 析构导致ds相关属性无法获取

    def addField(self, fieldName, fieldType, fieldValue=None):
        """
        shp属性表添加新字段
        :param fieldName: str: 字段名称，不区分大小写
        :param fieldType: ogr.OFT: 字段值类型(ogr.OFTInteger整型, OFTString字符串，OFTReal浮点型) TODO 支持更多数据类型
        :param fieldValue: list: 字段值
        :return:
        """

        self.readShp()  # 读取shp信息
        ds = ogr.Open(self.__shpPath, gdal.GA_Update)   # 更新模式打开
        lyr = ds.GetLayer()
        existFieldList = [x.upper() for x in self.getFieldName()]
        if fieldName.upper() in existFieldList:
            print("add field is exist.")
            return
        else:
            newField = ogr.FieldDefn(fieldName, fieldType)  # 创建字段
            lyr.CreateField(newField)  # 增加字段

        if fieldValue:  # 若传入字段值列表则赋值
            if len(fieldValue) != self.getFeatureCount():
                print("Wrong number of fieldVale")
                return
            else:
                for feature_index, each_feature in enumerate(lyr):
                    each_feature.SetField(fieldName, fieldValue[feature_index])
                    lyr.SetFeature(each_feature)    # 这一句话不加的话，属性是设置不了的
        ds.FlushCache()
        ds.Destroy()

    def deleteField(self, deleteField):
        """
        删除属性表某一列
        :param deleteField: str: 删除的列名
        :return:
        """
        if not isinstance(deleteField, str):
            raise TypeError('Argument Error: argument should be a str object not %r'
                            % type(deleteField))

        self.readShp()  # 读取shp信息
        fieldNameList = self.getFieldName()
        ds = ogr.Open(self.__shpPath, gdal.GA_Update)   # 更新模式打开
        lyr = ds.GetLayer()
        for i in range(len(fieldNameList)):
            if fieldNameList[i].upper() == deleteField.upper():  # 属性表名不区分大小写
                lyr.DeleteField(i)
        ds.FlushCache()
        ds.Destroy()

    def getExtent(self):
        """
        返回shp范围
        @return: 最小经度，最大经度，最小纬度，最大纬度
        """
        extend = self.__extent
        lonMin = extend[0]
        lonMax = extend[1]
        latMin = extend[2]
        latMax = extend[3]
        return {"xMin": lonMin, "xMax": lonMax, "yMin": latMin, "yMax": latMax}

    def getFieldName(self):
        """返回属性表字段名"""
        return self.__fieldName

    def getFieldInfo(self):
        """返回属性表字段信息"""
        return self.__fieldInfo

    def getFeatureCount(self):
        """返回属性表记录个数"""
        return self.__featureCount

    def getAttrTable(self):
        """返回属性表"""
        return self.__attrTable

    def getDs(self):
        """返回矢量dataset对象"""
        return self.__ds

    def getProjection(self):
        """返回矢量投影字符串 Wkt风格"""
        spatialRef = self.__layer.GetSpatialRef()
        return spatialRef.ExportToWkt()

    def __getGeomtry(self):
        # TODO：获取shp中地理信息
        pass

    def __getAttrTable(self):
        """
        :return:返回shp属性表记录信息，以pandas.DataFrame格式返回
        """
        layer = self.__layer

        info = {}   # 用一个字典接收属性表记录
        for field in self.__fieldName:
            info[field] = []        # 接受某列数据
            for i in range(self.__featureCount):
                feature = layer.GetFeature(i)
                info[field].append(str(feature.GetField(field)))
                # feature.Destroy()
        return pd.DataFrame(info)

    def __getFieldInfo(self):
        """
        :return:返回shp属性表字段信息，包含字段类型Type、最大字段宽度Width、字段数字精度Precision
        """
        defn = self.__layer.GetLayerDefn()
        fieldCount = defn.GetFieldCount()
        fieldInfo = {}
        for index in range(fieldCount):
            oField = defn.GetFieldDefn(index)
            fieldInfo[oField.GetNameRef()] = {"Type": oField.GetType(),
                                              "Width": oField.GetWidth(),
                                              "Precision": oField.GetPrecision()}
        return fieldInfo

    def __getFieldName(self):
        """
        :return:返回shp属性表字段名列表
        """
        defn = self.__layer.GetLayerDefn()
        fieldCount = defn.GetFieldCount()
        fieldName = []
        for index in range(fieldCount):
            oField = defn.GetFieldDefn(index)
            fieldName.append(oField.GetNameRef())
        return fieldName


if __name__ == "__main__":
    shpPath = r"C:\Users\wangbin\Desktop\test\B02000.shp"
    shpObj = ShapeFile(shpPath)
    shpObj.addField("top", ogr.OFTInteger)

    print("finish")