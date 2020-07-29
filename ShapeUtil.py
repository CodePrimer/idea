# -*- coding: utf-8  -*-
# -*- author: htht -*-

import os
import shutil
import pandas as pd
from BaseUtil import BaseUtil
import ogr
import gdal


class ShapeUtil(object):

    """矢量文件工具类"""

    def __init__(self):
        pass

    @staticmethod
    def copyFile(sourceFile, targetPath, targetName=None):
        """复制矢量文件"""
        # TODO 已存在的矢量文件会有警告信息，且不知是否会覆盖
        # TODO 编码问题导致复制后文件属性表乱码
        # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
        # gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 为了使属性表字段支持中文，请添加
        ds = ogr.Open(sourceFile)
        driver = ogr.GetDriverByName("ESRI Shapefile")
        pt_cp = driver.CopyDataSource(ds, targetPath)
        pt_cp.Release()
        copyShpPath = os.path.join(targetPath, os.path.basename(sourceFile))
        return copyShpPath

    @staticmethod
    def copyFile_os(sourceFile, targetPath, targetName=None):
        """复制文件，连带相关的文件"""
        # 类型检查
        if not isinstance(sourceFile, str):
            raise ValueError('sourceFile should be str')

        if not os.path.isfile(sourceFile):
            print("Copy Failed : SourceFile not exist.")
            return None
        # 分离文件名和后缀
        filePath = BaseUtil.file_path_info(sourceFile)[0]
        fileBasename = BaseUtil.file_name(sourceFile, ext=False)

        if targetName:
            saveBaseName = targetName
        else:
            saveBaseName = fileBasename
        copyShpPath = os.path.join(targetPath, saveBaseName + ".shp")

        # 查看文件类型和对应的相关文件
        relatedSuffix = ['.dbf', '.prj', '.shp', '.shx', '.cpg', '.sbn', '.sbx', '.shp.xml']

        # 拷贝文件
        for suffix in relatedSuffix:
            oldFilePath = os.path.join(filePath, fileBasename + suffix)
            if os.path.exists(oldFilePath):
                newFileName = saveBaseName + suffix
                BaseUtil.copy_file(oldFilePath, targetPath, target_name=newFileName)

        return copyShpPath

    @staticmethod
    def pointToCsv(shpPath, csvPath, zField):
        """
        点矢量转换为csv   TODO csv文件规范待完善
        :param shpPath: str 矢量文件路径
        :param csvPath: str 保存csv文件路径
        :param zField: str 保存的属性字段
        :return:
        """
        try:
            gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
            gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 为了使属性表字段支持中文，请添加
            ogr.RegisterAll()  # 注册所有的驱动
            driver = ogr.GetDriverByName("ESRI Shapefile")  # 数据格式的驱动
            ds = driver.Open(shpPath)
            if ds is None:
                return
            layer = ds.GetLayer(0)

            xList = []
            yList = []
            zList = []

            for i in range(layer.GetFeatureCount()):
                feature = layer.GetFeature(i)
                geom = feature.GetGeometryRef()
                x = str(geom.GetX())  # 读取xy坐标
                y = str(geom.GetY())
                z = feature.GetField(zField)
                xList.append(x)
                yList.append(y)
                zList.append(z)
                feature.Destroy()

            pdTable = pd.DataFrame({"x": xList, "y": yList, "z": zList})
            pdTable.to_csv(csvPath, index=None, header=None)
        except Exception as e:
            print(e)


