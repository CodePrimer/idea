# -*- coding: utf-8  -*-

import os
import time
import gdal
import ogr
import pandas as pd
import numpy as np


"""
    静态函数方式实现分区特征值、分级面积、分级面积百分比统计功能
    
    测试环境：
    python3.7.3 
        numpy 1.18.0
        gdal 3.0.1
        pandas 0.25.3 
"""


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
        TODO 后续函数依赖于readShp
        :return:
        """
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
        gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 为了使属性表字段支持中文，请添加
        ogr.RegisterAll()  # 注册所有的驱动
        driver = ogr.GetDriverByName("ESRI Shapefile")  # 数据格式的驱动
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
                feature.Destroy()
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


class BaseUtil(object):

    @staticmethod
    def timestamp():
        return str(int(time.time() * 100))

    @staticmethod
    def file_path_info(file_path):
        """
        获取文件路径，文件名(无后缀)，文件扩展名
        :param file_path: str: 文件路径 # TODO 文件夹路径如何过滤
        :return:list
        """
        file_dir = os.path.dirname(file_path)
        file_name = BaseUtil.file_name(file_path, ext=False)
        file_ext = BaseUtil.file_ext(file_path)
        return [file_dir, file_name, file_ext]

    @staticmethod
    def file_name(file_path, ext=True):
        """
        获取文件名
        :param file_path: str: 文件路径 # TODO 文件夹路径如何过滤
        :param ext: bool: True-返回值带文件类型 False-返回值不带文件类型
        :return: str
        """
        base_name = os.path.basename(file_path)
        if not ext:
            split_list = base_name.split(".")
            split_list.pop()
            return ".".join(split_list)
        else:
            return base_name

    @staticmethod
    def file_ext(file_path):
        """
        获取文件扩展类型
        :param file_path: str: 文件路径
        :return:str
        """
        try:
            ext = os.path.splitext(file_path)[1]
            return ext
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def copy_file(source_file, target_dir, target_name=None):
        """
        复制文件
        :param source_file: 被复制文件路径
        :param target_dir: 目标文件夹
        :param target_name: 复制后文件名（默认不变）
        :return: True - 执行成功 False - 执行失败
        """
        if not os.path.isfile(source_file):
            print("被复制文件不存在.")
            return False
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        try:
            if target_name:
                save_name = target_name
            else:
                save_name = os.path.basename(source_file)
            target_file_path = os.path.join(target_dir, save_name)
            if not os.path.exists(target_file_path) or (
                    os.path.exists(target_file_path) and (
                    os.path.getsize(target_file_path) != os.path.getsize(source_file))):
                with open(target_file_path, "wb") as ft:
                    with open(source_file, "rb") as fs:
                        ft.write(fs.read())
            return True
        except Exception as e:
            print(e)
            return False


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


class GdalUtil(object):
    @staticmethod
    def raster_clip_by_shp(in_path, out_path, shp_path, nodata_val=-9999):
        """
        依据shp边界对栅格数据进行裁切，输出TIF投影和输入TIF投影一致

        :param in_path: str: 栅格文件路径
        :param out_path: str: 输出栅格文件路径  若设置为空字符串则默认以MEM模式输出
        :param shp_path: str: 矢量文件路径
        :param nodata_val: float: 背景值
        :return:
        """
        try:
            shp_obj = ShapeFile(shp_path)
            shp_obj.readShp()
            shp_extend = shp_obj.getExtent()  # 获取矢量经纬度范围

            tif_obj = GeoTiffFile(in_path)
            tif_obj.readTif()
            x_res = tif_obj.getXRes()  # 获取栅格分辨率
            y_res = tif_obj.getYRes()

            out_bounds = (shp_extend["xMin"], shp_extend["yMin"], shp_extend["xMax"], shp_extend["yMax"])

            if out_path == '':
                ds = gdal.Warp(out_path, in_path, format='MEM', outputBounds=out_bounds, dstNodata=nodata_val,
                               cropToCutline=False, xRes=x_res, yRes=y_res)
            else:
                ds = gdal.Warp(out_path, in_path, format='GTiff', outputBounds=out_bounds, dstNodata=nodata_val,
                               cropToCutline=False, xRes=x_res, yRes=y_res)
            return ds

        except Exception as e:
            print(e)
            return False

    @staticmethod
    def shape_rasterize(shp_path, out_path, tif_path):
        """
        统计矢量转换为栅格
        :param shp_path: 转换矢量
        :param out_path: 输出路径 若设置为空字符串则默认以MEM模式输出
        :param tif_path: 为转栅格提供xy向分辨率
        :return:
        """
        tif_obj = GeoTiffFile(tif_path)
        tif_obj.readTif()
        x_res = tif_obj.getXRes()
        y_res = tif_obj.getYRes()
        shp_obj = ShapeFile(shp_path)
        shp_obj.readShp()
        shp_extend = shp_obj.getExtent()
        out_bounds = (shp_extend["xMin"], shp_extend["yMin"], shp_extend["xMax"], shp_extend["yMax"])

        if out_path == '':
            options = gdal.RasterizeOptions(outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=65535,
                                            attribute="obj_id", useZ=False, xRes=x_res, yRes=y_res, format="MEM")
            ds = gdal.Rasterize(out_path, shp_path, options=options)
        else:
            options = gdal.RasterizeOptions(outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=65535,
                                            attribute="obj_id", useZ=False, xRes=x_res, yRes=y_res, format="GTiff")
            ds = gdal.Rasterize(out_path, shp_path, options=options)
        return ds


class Statistic(object):

    @staticmethod
    def pixAreaSum(lonList, latList, xRes, yRes):
        """
        计算栅格总面积
        :param lonList: 经度列表
        :param latList: 纬度列表
        :param xRes: x向分辨率
        :param yRes: y向分辨率
        :return: 列表内所有像元面积总和
        """
        pixAreaArray = Statistic.haversine(lonList, latList, xRes, 0) * Statistic.haversine(lonList, latList, 0, yRes)
        return np.sum(pixAreaArray)

    @staticmethod
    def haversine(lon, lat, dlon, dlat):
        """计算像元经纬度距离"""
        # 将十进制度数转化为弧度
        lon, lat, dlon, dlat = (np.radians(iparam) for iparam in (lon, lat, dlon, dlat))
        # haversine公式
        a = np.sin(dlat / 2) ** 2 + np.cos(lat) * np.cos(lat + dlat) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371.393  # 地球平均半径，单位为公里
        return c * r

    @staticmethod
    def copy_shp_file(source_file, target_dir):

        """
        复制shp文件，连带相关的文件
        :param source_file: 被复制shp文件
        :param target_dir: 复制到的目标文件夹
        :return: 复制后shp路径
        """
        # 类型检查
        if not isinstance(source_file, str):
            return
        if not os.path.isfile(source_file):
            print('source file not exist.')
            return

        # 分离文件名和后缀
        file_path = BaseUtil.file_path_info(source_file)[0]
        file_basename = BaseUtil.file_name(source_file, ext=False)

        save_basename = file_basename
        copy_shp_path = os.path.join(target_dir, save_basename + ".shp")

        # 查看文件类型和对应的相关文件
        related_suffix = ['.dbf', '.prj', '.shp', '.shx', '.cpg', '.sbn', '.sbx', '.shp.xml']

        # 拷贝文件
        for suffix in related_suffix:
            old_file_path = os.path.join(file_path, file_basename + suffix)
            if os.path.exists(old_file_path):
                new_file_name = save_basename + suffix
                BaseUtil.copy_file(old_file_path, target_dir, target_name=new_file_name)
        return copy_shp_path

    @staticmethod
    def shp_handel(shp_path, field_name):
        """
        shp属性表标准化操作
        :return: 返回shp字段和obj_id映射字典
        """
        shp_obj = ShapeFile(shp_path)
        shp_obj.readShp()
        # 删除非关键字属性字段
        field_name_list = shp_obj.getFieldName()
        field_name_list.pop(field_name_list.index(field_name))
        for each in field_name_list:
            shp_obj.deleteField(each)
        # 对临时shp文件添加唯一标识
        shpObjId = np.arange(shp_obj.getFeatureCount()).tolist()
        shp_obj.addField("obj_id", ogr.OFTInteger, fieldValue=shpObjId)
        # 建立obj_ID与统计标识映射字典
        shp_obj.readShp()
        attrInfo = shp_obj.getAttrTable()
        relation_dict = dict(zip(attrInfo["obj_id"], attrInfo[field_name]))
        return relation_dict

    @staticmethod
    def statistic_character(product_ds, region_ds, id_dict, value_range):
        """
        特征值统计   ['MAX', 'MIN', 'MEAN', 'STD', 'SUM']
        :param product_ds: 产品数据集
        :param region_ds: 区域数据集
        :param id_dict: id与obj_id对应关系
        :param value_range: 有效值范围
        :return:
        """
        # 1.对有效值区间范围外的赋值np.nan
        product_arr = product_ds.GetRasterBand(1).ReadAsArray()
        product_arr = product_arr.astype(np.float)  # 转换为浮点型，否则整形数组无法赋值nan
        nan_loc = np.logical_or(product_arr < value_range[0], product_arr > value_range[1])
        product_arr[nan_loc] = np.nan

        character_result = {}
        # 2.循环各区域计算
        region_arr = region_ds.GetRasterBand(1).ReadAsArray()
        for obj_id in id_dict.keys():
            # 初始化统计结果，特征值初始值为np.nan
            cur_sta_result = {'MAX': np.nan, 'MIN': np.nan, 'MEAN': np.nan, 'STD': np.nan, 'SUM': np.nan}
            cur_product_arr = product_arr[region_arr == int(obj_id)]
            if cur_product_arr.size == 0:  # TODO 矢量中某些斑块面积小于分辨率，导致矢量栅格化时被忽略，这种斑块统计跳过
                continue
            cur_sta_result["MAX"] = np.nanmax(cur_product_arr)
            cur_sta_result["MIN"] = np.nanmin(cur_product_arr)
            cur_sta_result["MEAN"] = np.nanmean(cur_product_arr)
            cur_sta_result['STD'] = np.nanstd(cur_product_arr)
            cur_sta_result['SUM'] = np.nansum(cur_product_arr)
            character_result[id_dict[obj_id]] = cur_sta_result

        return character_result

    @staticmethod
    def statistic_reclassify_PROJCS(product_ds, region_ds, id_dict, value_range, reclass_dict):
        """
        等面积分级面积统计，包括面积占比
        :param product_ds: 产品数据集
        :param region_ds: 区域数据集
        :param id_dict: id与obj_id对应关系
        :param value_range: 有效值范围
        :param reclass_dict: 重分类字典 {'等级1': [等级最小值, 等级最大值]}  值域区间左开右闭
        :return:
        """
        # 1.对有效值区间范围外的赋值np.nan
        product_arr = product_ds.GetRasterBand(1).ReadAsArray()
        product_arr = product_arr.astype(np.float)  # 转换为浮点型，否则整形数组无法赋值nan
        nan_loc = np.logical_or(product_arr < value_range[0], product_arr > value_range[1])
        product_arr[nan_loc] = np.nan

        # 2.计算经纬度矩阵，为计算面积做准备
        geotrans = product_ds.GetGeoTransform()
        # TODO 等面积投影获取像元面积大小
        x_res = abs(geotrans[1]) / 1000     # 单位: 千米
        y_res = abs(geotrans[5]) / 1000     # 单位: 千米
        pixel_area = x_res * y_res

        area_result = {}        # 面积结果
        percent_result = {}     # 百分比结果
        # 3.循环各区域计算
        region_arr = region_ds.GetRasterBand(1).ReadAsArray()
        temp_dict = dict.fromkeys(reclass_dict.keys(), 0)
        for obj_id in id_dict.keys():
            # 先计算当前区域面积
            cur_region_loc = region_arr == int(obj_id)
            # 计算当前区域面积  TODO 当前区域面积等于当前区域像元数乘像元面积
            cur_region_area = len(region_arr[region_arr == int(obj_id)]) * pixel_area
            # TODO 矢量中某些斑块面积小于分辨率，导致矢量栅格化时被忽略，这种斑块统计跳过
            if cur_region_area == 0:
                continue
            cur_region_prod = np.where(cur_region_loc, product_arr, np.nan)  # 当前区域产品数组
            cur_area_result = temp_dict.copy()  # 当前区域的各等级面积结果
            cur_percent_result = temp_dict.copy()       # 当前区域的各等级面积百分比结果
            for level in reclass_dict.keys():
                minV = reclass_dict[level][0]
                maxV = reclass_dict[level][1]
                level_loc = (cur_region_prod > minV) & (cur_region_prod <= maxV)
                temp_count_list = cur_region_prod[level_loc].tolist()
                cur_level_area = len(temp_count_list) * pixel_area
                cur_area_result[level] = cur_level_area
                cur_percent_result[level] = cur_level_area/cur_region_area * 100     # 计算面积占比
            area_result[id_dict[obj_id]] = cur_area_result
            percent_result[id_dict[obj_id]] = cur_percent_result

        return area_result, percent_result

    @staticmethod
    def statistic_reclassify_GEOGCS(product_ds, region_ds, id_dict, value_range, reclass_dict):
        """
        等经纬分级面积统计，包括面积占比
        :param product_ds: 产品数据集
        :param region_ds: 区域数据集
        :param id_dict: id与obj_id对应关系
        :param value_range: 有效值范围
        :param reclass_dict: 重分类字典 {'等级1': [等级最小值, 等级最大值]}  值域区间左开右闭
        :return:
        """
        # 1.对有效值区间范围外的赋值np.nan
        product_arr = product_ds.GetRasterBand(1).ReadAsArray()
        product_arr = product_arr.astype(np.float)  # 转换为浮点型，否则整形数组无法赋值nan
        nan_loc = np.logical_or(product_arr < value_range[0], product_arr > value_range[1])
        product_arr[nan_loc] = np.nan

        # 2.计算经纬度矩阵，为计算面积做准备
        geotrans = product_ds.GetGeoTransform()
        lon_list = np.arange(product_arr.shape[1]) * geotrans[1] + geotrans[0]
        lat_list = np.arange(product_arr.shape[0]) * geotrans[5] + geotrans[3]
        lon_array = np.array([lon_list.tolist()] * product_arr.shape[0])
        lat_array = np.array([lat_list.tolist()] * product_arr.shape[1]).transpose()
        x_res = abs(geotrans[1])
        y_res = abs(geotrans[5])

        area_result = {}        # 面积结果
        percent_result = {}     # 百分比结果
        # 3.循环各区域计算
        region_arr = region_ds.GetRasterBand(1).ReadAsArray()
        temp_dict = dict.fromkeys(reclass_dict.keys(), 0)
        for obj_id in id_dict.keys():
            # 先计算当前区域面积
            cur_region_loc = region_arr == int(obj_id)
            # 计算当前区域面积
            cur_lon_list = lon_array[cur_region_loc].tolist()  # 当前区域经度列表
            cur_lat_list = lat_array[cur_region_loc].tolist()  # 当前区域纬度列表
            cur_region_area = Statistic.pixAreaSum(cur_lon_list, cur_lat_list, x_res, y_res)    # 当前区域面积
            cur_region_prod = np.where(cur_region_loc, product_arr, np.nan)  # 当前区域产品数组
            cur_area_result = temp_dict.copy()  # 当前区域的各等级面积结果
            cur_percent_result = temp_dict.copy()       # 当前区域的各等级面积百分比结果
            for level in reclass_dict.keys():
                minV = reclass_dict[level][0]
                maxV = reclass_dict[level][1]
                level_loc = (cur_region_prod > minV) & (cur_region_prod <= maxV)
                temp_lon_list = lon_array[level_loc].tolist()
                temp_lat_list = lat_array[level_loc].tolist()
                cur_level_area = Statistic.pixAreaSum(temp_lon_list, temp_lat_list, x_res, y_res)   # 当前区域当前等级面积
                cur_area_result[level] = cur_level_area
                cur_percent_result[level] = cur_level_area/cur_region_area * 100     # 计算面积占比
            area_result[id_dict[obj_id]] = cur_area_result
            percent_result[id_dict[obj_id]] = cur_percent_result

        return area_result, percent_result

    @staticmethod
    def check_projection(tif_path, shp_path):
        # 获取栅格和矢量投影字符串
        tif_obj = GeoTiffFile(tif_path)
        tif_obj.readTif()
        tif_prj = tif_obj.getProj()
        shp_obj = ShapeFile(shp_path)
        shp_obj.readShp()
        shp_prj = shp_obj.getProjection()

        if tif_prj[0: 6] != shp_prj[0: 6]:
            print('栅格文件和矢量文件投影不匹配')
            return None
        else:
            return tif_prj[0: 6]

    @staticmethod
    def main(tif_path, shp_path, temp_dir, field_name, value_range, statistic_mode, reclass_dict=None):
        """
        输入参数
        :param tif_path: str 统计栅格文件路径
        :param shp_path: str 统计矢量文件路径
        :param temp_dir: str 临时文件夹路径
        :param field_name: str 统计矢量关键字段
        :param value_range: list 栅格文件有效值范围 [最小值, 最大值] 左开右闭
        :param statistic_mode: int 三种统计类型: 1仅特征值统计 2仅分级面积统计 3两者都统计
        :param reclass_dict: dict 重分类字典，若进行分级面积统计必须传参，参数格式：{'等级1': [等级最小值, 等级最大值]} 左开右闭
        :return:
            返回值以字典形式
            根据统计类型不同返回值内容不同
            仅特征值统计时
                return_value = {'CHAR': {'ID1': {特征值字典}, 'ID2': {特征值字典}}}
            仅分级面积统计时
                return_value = {'AREA': {'ID1': {'等级面积字典'}, 'ID2': {'等级面积字典'}},
                                'PERC': {'ID1': {'等级百分比字典'}, 'ID2': {'等级百分比字典'}}}
            两者都统计时
                return_value = {'CHAR': {'ID1': {特征值字典}, 'ID2': {特征值字典}},
                                'AREA': {'ID1': {'等级面积字典'}, 'ID2': {'等级面积字典'}},
                                'PERC': {'ID1': {'等级百分比字典'}, 'ID2': {'等级百分比字典'}}}
        """

        # 1.备份矢量文件到临时文件夹，防止损坏原始文件和多线程冲突
        backup_shp_path = Statistic.copy_shp_file(shp_path, temp_dir)
        # 2.处理矢量，建立区域ID和obj_id对应关系
        id_dict = Statistic.shp_handel(backup_shp_path, field_name)

        # 3.获取矢量和栅格投影坐标的单位
        proj_type = Statistic.check_projection(tif_path, shp_path)
        if proj_type is None:
            return None

        # 4.矢量裁切栅格，product_ds为裁切后返回的dataset
        clip_tif = os.path.join(temp_dir, BaseUtil.file_name(shp_path, ext=False) + '_clip_' + BaseUtil.timestamp() + '.tif')
        product_ds = GdalUtil.raster_clip_by_shp(tif_path, clip_tif, shp_path)
        # 5.矢量按区域栅格化，region_ds为矢量栅格化后返回的dataset
        rasterize_tif = os.path.join(temp_dir, BaseUtil.file_name(shp_path, ext=False) + '_rasterize_' + BaseUtil.timestamp() + '.tif')
        region_ds = GdalUtil.shape_rasterize(backup_shp_path, rasterize_tif, tif_path)
        # TODO 进行行列号检验，后期考虑删除
        if product_ds.RasterXSize != region_ds.RasterXSize or product_ds.RasterYSize != region_ds.RasterYSize:
            print("行列号不一致.")
            return None

        if statistic_mode == 2 or statistic_mode == 3:
            if reclass_dict is None:
                print('缺少重分类信息')
                return None

        statistic_result = {}

        if statistic_mode == 1 or statistic_mode == 3:
            character_result = Statistic.statistic_character(product_ds, region_ds, id_dict, value_range)
            statistic_result['CHAR'] = character_result
        if statistic_mode == 2 or statistic_mode == 3:
            # 等面积投影计算函数
            if proj_type == 'PROJCS':
                reclassa_result, reclassp_result = Statistic.statistic_reclassify_PROJCS(product_ds, region_ds, id_dict,
                                                                                         value_range,
                                                                                         reclass_dict)
                statistic_result['AREA'] = reclassa_result
                statistic_result['PERC'] = reclassp_result
            # 等经纬投影计算函数
            elif proj_type == 'GEOGCS':
                reclassa_result, reclassp_result = Statistic.statistic_reclassify_GEOGCS(product_ds, region_ds, id_dict,
                                                                                         value_range,
                                                                                         reclass_dict)
                statistic_result['AREA'] = reclassa_result
                statistic_result['PERC'] = reclassp_result
            else:
                pass

        return statistic_result


if __name__ == '__main__':

    in_tif_path = r'C:\Users\Think\Desktop\output\result_quxian.tif'
    in_shp_path = r'C:\Users\Think\Desktop\nongyemianyuan\shp\320500_quxian.shp'
    in_temp_dir = r'C:\Users\Think\Desktop\temp'
    in_field_name = 'id'
    in_value_range = [0, 10]
    statistic_mode = 1

    result = Statistic.main(in_tif_path, in_shp_path, in_temp_dir, in_field_name, in_value_range, statistic_mode)
    for each in result['CHAR'].keys():
        string = '%s : %s' % (each, str(result['CHAR'][each]['MEAN']))
        print(string)
    print('finish')
