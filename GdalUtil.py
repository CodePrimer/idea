# -*- coding: utf-8  -*-
# -*- author: htht -*-

import os
import gdal
from osgeo import osr
from osgeo import ogr
import pandas as pd
import numpy as np
from GeoTiffFile import GeoTiffFile
from BaseUtil import BaseUtil
from XmlUtil import XmlUtil
from ShapeFile import ShapeFile
from ShapeUtil import ShapeUtil


class GdalUtils(object):
    """新版gdal工具类 去除自封装类的依赖"""

    @staticmethod
    def PolygonToRaster(in_path, out_path, x_res, y_res, field_name, out_bounds=None, no_data=65535):
        """
        面矢量转为栅格
        :param in_path: str 输入矢量文件路径
        :param out_path: str 输出栅格文件路径
        :param x_res: float 输出栅格x向分辨率
        :param y_res: float 输出栅格y向分辨率
        :param field_name: str 栅格赋值的矢量字段名
        :param out_bounds: tuple 输出栅格范围  [xmin, ymin, xmax, ymax]
        :param no_data: int 无效值大小
        :return:
        """
        try:
            if not out_bounds:
                gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
                gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 为了使属性表字段支持中文，请添加
                ogr.RegisterAll()  # 注册所有的驱动
                layer = ogr.Open(in_path, gdal.GA_ReadOnly).GetLayer(0)
                shp_extent = layer.GetExtent()
                out_bounds = (shp_extent[0], shp_extent[2], shp_extent[1], shp_extent[3])

            options = gdal.RasterizeOptions(outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=no_data,
                                            attribute=field_name, useZ=False, xRes=x_res, yRes=y_res, format="GTiff")
            ds = gdal.Rasterize(out_path, in_path, options=options)

            if not ds:
                return False
            del ds
            return True

        except Exception as e:
            print(e)
            return False



class Grid(object):

    """gdal插值工具类"""

    def __init__(self):
        pass

    @staticmethod
    def invdist(in_path, out_path, field_name, output_bounds=None, param=None):
        """
        反距离加权插值 将shp文件插值为TIF
        :param in_path: 输入shp文件
        :param out_path: 输出tif文件
        :param field_name: 被插值的属性字段
        :param output_bounds: 输出tif四角范围 (xmin, ymin, xmax, ymax) 默认为点shp四角坐标
        :param param: 插值参数，字符串，不传参以默认值进行
                                [ power：加权系数（默认为3.0）,
                                smoothing：平滑参数（默认为0.0）,
                                radius1：搜索椭圆的第一个半径（如果旋转角度为0，则为X轴），将此参数设置为零以使用整个点数组（默认值为0.0）,
                                radius2：搜索椭圆的第二个半径（如果旋转角度为0，则为Y轴），将此参数设置为零以使用整个点数组（默认值为0.0）,
                                angle：搜索椭圆的旋转角度，以度为单位（逆时针，默认为0.0）,
                                max_points：要使用的最大数据点数。搜索的点数不要超过此数字。仅在设置搜索椭圆（两个半径都不为零）时使用。零表示应使用所有找到的点（默认值为0）,
                                min_points：要使用的最小数据点数。如果发现的点数量较少，则网格节点被认为是空的，并将被NODATA标记填充。仅在设置搜索椭圆（两个半径都不为零）时使用（默认值为0）,
                                nodata：NODATA标记以填充空白点（默认为0.0）]
        :return:
        """
        if param:
            if len(param) != 8 or not all(isinstance(x, str) for x in param):
                print('input param format error.')
                return
            else:
                param_str = 'invdist'
                param_str += ':power=' + param[0]
                param_str += ':smoothing=' + param[1]
                param_str += ':radius1=' + param[2]
                param_str += ':radius2=' + param[3]
                param_str += ':angle=' + param[4]
                param_str += ':max_points=' + param[5]
                param_str += ':min_points=' + param[6]
                param_str += ':nodata=' + param[7]

        else:
            param_str = 'invdist:power=3.0:smoothing=0.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0'
        if output_bounds:
            options = gdal.GridOptions(algorithm=param_str, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name,
                                       outputBounds=output_bounds)
        else:
            options = gdal.GridOptions(algorithm=param_str, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name)

        gdal.Grid(destName=out_path, srcDS=in_path, options=options)

    @staticmethod
    def invdistnn(in_path, out_path, field_name, output_bounds=None, param=None):
        """
        最邻近反距离加权插值 将shp文件插值为TIF
        :param in_path: 输入的shp文件
        :param out_path: 输出的tif文件
        :param field_name: 被插值的属性字段
        :param output_bounds: 输出的tif四角范围 (xmin, ymin, xmax, ymax)
        :param param: 插值参数，字符串，不传参以默认值进行
                    [power：加权系数（默认为3.0）
                    smoothing：平滑参数（默认为0.0）
                    radius：搜索圆的半径，不应为零（默认值为1.0）
                    max_points：要使用的最大数据点数。搜索的点数不要超过此数字。 加权时，发现的点将从最远到最远的距离排名（默认值为12）
                    min_points：要使用的最小数据点数。如果发现的点数量较少，则网格节点被认为是空的，并将被NODATA标记填充（默认值为0）
                    nodata：NODATA标记以填充空白点（默认为0.0）]
        :return:
        """

        # TODO 是否为密集点时比较试用？
        # TODO radius设置太小会导致数据镂空
        if param:
            if len(param) != 6 or not all(isinstance(x, str) for x in param):
                print('input param format error.')
                return
            else:
                param_str = 'invdistnn'
                param_str += ':power=' + param[0]
                param_str += ':smoothing=' + param[1]
                param_str += ':radius=' + param[2]
                param_str += ':max_points=' + param[3]
                param_str += ':min_points=' + param[4]
                param_str += ':nodata=' + param[5]
        else:
            param = 'invdistnn:power=3.0:smoothing=0.0:radius=1.0:max_points=0:min_points=0:nodata=0.0'
        if output_bounds:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name,
                                       outputBounds=output_bounds)
        else:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name)

        gdal.Grid(destName=out_path, srcDS=in_path, options=options)

    @staticmethod
    def average(in_path, out_path, field_name, output_bounds=None, param=None):
        """
        移动平均法 将shp文件插值为TIF
        :param in_path: 输入的shp文件
        :param out_path: 输出的tif文件
        :param field_name: 被插值的属性字段
        :param output_bounds: 输出的tif四角范围 (xmin, ymin, xmax, ymax)
        :param param: 插值参数，字符串，不传参以默认值进行
                    [ radius1：搜索椭圆的第一个半径（如果旋转角度为0，则为X轴）。将此参数设置为零以使用整个点数组（默认值为0.0）
                    radius2：搜索椭圆的第二个半径（如果旋转角度为0，则为Y轴）。将此参数设置为零以使用整个点数组（默认值为0.0）
                    angle：搜索椭圆的旋转角度，以度为单位（逆时针，默认为0.0）
                    min_points：要使用的最小数据点数。 如果发现的点数量较少，则网格节点被认为是空的，并将被NODATA标记填充（默认值为0）
                    nodata：NODATA标记以填充空白点（默认为0.0）]
        :return:
        """

        # TODO 有问题？？

        if param:
            if len(param) != 5 or not all(isinstance(x, str) for x in param):
                print('input param format error.')
                return
            else:
                param_str = 'average'
                param_str += ':radius1=' + param[0]
                param_str += ':radius2=' + param[1]
                param_str += ':angle=' + param[2]
                param_str += ':min_points=' + param[3]
                param_str += ':nodata=' + param[4]
        else:
            param = 'average:radius1=1:radius2=1:angle=0.0:min_points=0:nodata=0.0'
        if output_bounds:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name,
                                       outputBounds=output_bounds)
        else:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name)

        gdal.Grid(destName=out_path, srcDS=in_path, options=options)

    @staticmethod
    def nearest(in_path, out_path, field_name, output_bounds=None, param=None):
        """
        最邻近法 将shp文件插值为TIF
        :param in_path: 输入的shp文件
        :param out_path: 输出的tif文件
        :param field_name: 被插值的属性字段
        :param output_bounds: 输出的tif四角范围 (xmin, ymin, xmax, ymax)
        :param param: 插值参数，字符串，不传参以默认值进行
                    [radius1：搜索椭圆的第一个半径（如果旋转角度为0，则为X轴）。将此参数设置为零以使用整个点数组（默认值为0.0）
                    radius2：搜索椭圆的第二个半径（如果旋转角度为0，则为Y轴）。将此参数设置为零以使用整个点数组（默认值为0.0）
                    angle：搜索椭圆的旋转角度，以度为单位（逆时针，默认为0.0）
                    nodata：NODATA标记以填充空白点（默认为0.0）]
        :return:
        """
        if param:
            if len(param) != 4 or not all(isinstance(x, str) for x in param):
                print('input param format error.')
                return
            else:
                param_str = 'nearest'
                param_str += ':radius1=' + param[0]
                param_str += ':radius2=' + param[1]
                param_str += ':angle=' + param[2]
                param_str += ':nodata=' + param[3]
        else:
            param = 'nearest:radius1=0.0:radius2=0.0:angle=0.0:nodata=0.0'
        if output_bounds:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name,
                                       outputBounds=output_bounds)
        else:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name)

        gdal.Grid(destName=out_path, srcDS=in_path, options=options)

    @staticmethod
    def linear(in_path, out_path, field_name, output_bounds=None, param=None):
        """
        线性法 将shp文件插值为TIF
        :param in_path: 输入的shp文件
        :param out_path: 输出的tif文件
        :param field_name: 被插值的属性字段
        :param output_bounds: 输出的tif四角范围 (xmin, ymin, xmax, ymax)
        :param param: 插值参数，字符串，不传参以默认值进行
                    [radius:如果要插入的点不适合Delaunay三角剖分的三角形，请使用该最大距离搜索最近的邻居，否则使用nodata
                            如果设置为-1，则搜索距离是无限的
                            如果设置为0，则将始终使用nodata值。默认值为-1
                    nodata：NODATA标记以填充空白点（默认为0.0）]
        :return:
        """
        # TODO 外扩性不太好
        if param:
            if len(param) != 2 or not all(isinstance(x, str) for x in param):
                print('input param format error.')
                return
            else:
                param_str = 'linear'
                param_str += ':radius=' + param[0]
                param_str += ':nodata=' + param[1]
        else:
            param = 'linear:radius=-1:nodata=0.0'
        if output_bounds:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name,
                                       outputBounds=output_bounds)
        else:
            options = gdal.GridOptions(algorithm=param, format="GTiff", outputType=gdal.GDT_Float32, zfield=field_name)

        gdal.Grid(destName=out_path, srcDS=in_path, options=options)


class GdalUtil(object):

    """GDAL工具类"""

    @staticmethod
    def MRT(input_list, output_file, ds_name, res, prj_info='EPSG:4326'):
        """
        实现 MODIS HDF 文件 拼接投影转换功能
        :param input_list: 输入hdf文件列表
        :param output_file: 输出栅格路径
        :param ds_name: 目标数据集名字
        :param res: 输出分辨率大小
        :param prj_info: str: 重投影信息 可使用三种形式：
                type1 投影编码 : "EPSG:4326", "EPSG:4490"
                type2 prj文件路径 : "./GCS_WGS_1984.prj"
                type3 投影信息字符串 : 'GEOGCS["GCS_WGS_1984",
                                      DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],
                                      PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        """

        def get_hdf_index(hdf_file, target_name):
            """
            获取hdf文件中目标数据集所在索引
            """
            ds = gdal.Open(hdf_file)
            sub_ds = ds.GetSubDatasets()
            # 获取目标数据集的信息
            target_ds = list(filter(lambda x: target_name in str(x), sub_ds))
            try:
                # 得到目标数据集索引
                target_index = sub_ds.index(target_ds[0])
                return target_index
            except IndexError:
                print('Error: please check correctness of "target_name" ')

        # 获取目标数据集索引
        target_index = get_hdf_index(input_list[0], ds_name)
        # 获取目标数据集
        target_list = []
        for each_file in input_list:
            ds = gdal.Open(each_file)
            sub_ds = ds.GetSubDatasets()
            target_list.append(sub_ds[target_index][0])
        # 拼接、投影转换
        gdal.Warp(output_file, target_list, dstSRS=prj_info, format='GTiff', xRes=res, yRes=res)

    @staticmethod
    def rasterSynthesis(inputFileList, outputPath, mode, valueRange, bgValue=-9999, extent=None, res=None):
        """
        单波段栅格文件最大/最小/均值合成功能
        默认输入文件分辨率和经纬度范围一致
        也可指定经纬度范围和分辨率进行重采样，参数(extent, res)

        :param inputFileList: list 输入文件路径列表，文件之间以","隔开
        :param outputPath: str 合成输出文件路径
        :param mode: str 合成方法 可选参数 ("mean", "max", "min")
        :param valueRange: list 合成有效值范围 e.g [-1,1]
        :param bgValue: float 合成结果中无效值设定 默认-9999
        :param extent: 输出文件经纬度范围 默认与第一个文件保持一致 {"xMin": lonMin, "xMax": lonMax, "yMin": latMin, "yMax": latMax}
        :param res: float 输出文件分辨率 默认与第一个文件保持一致
        :return:
        """

        try:
            sampleTifObj = GeoTiffFile(inputFileList[0])
            sampleTifObj.readTif()

            # 判断参数是否指定经纬度范围和分辨率
            if extent is None:
                extentInfo = sampleTifObj.getGeoExtent()
            else:
                extentInfo = extent
            if res is None:
                resInfo = sampleTifObj.getXRes()
            else:
                resInfo = res

            # 获取输出行列号
            warpDs = GdalUtil.raster_warp(inputFileList[0], "", extentInfo, resInfo, mode="MEM")
            if warpDs is None:
                return None
            width = warpDs.RasterXSize
            height = warpDs.RasterYSize
            trans = warpDs.GetGeoTransform()
            proj = warpDs.GetProjection()
            del warpDs

            # 三种合成方式max/min/mean
            # 1.mean
            if mode.upper() == "MEAN":
                countArray = np.zeros((height, width), dtype=np.uint16)  # 计数器
                sumArray = np.zeros((height, width), dtype=np.float32)  # 总和
                for f in inputFileList:
                    warpDs = GdalUtil.raster_warp(f, "", extentInfo, resInfo, mode="MEM")
                    array = warpDs.GetRasterBand(1).ReadAsArray()
                    loc = np.logical_and(array > valueRange[0], array <= valueRange[1])
                    countArray[loc] = countArray[loc] + 1
                    sumArray[loc] = sumArray[loc] + array[loc]

                outArray = sumArray / countArray
                outArray[countArray == 0] = bgValue

            # 2.max
            elif mode.upper() == "MAX":
                outArray = np.ones((height, width), dtype=np.float32) * valueRange[0]
                for f in inputFileList:
                    warpDs = GdalUtil.raster_warp(f, "", extentInfo, resInfo, mode="MEM")
                    array = warpDs.GetRasterBand(1).ReadAsArray()
                    array = array.astype(np.float32)
                    nanLoc = np.logical_or(array <= valueRange[0], array > valueRange[1])
                    array[nanLoc] = np.nan
                    loc = array > outArray
                    outArray[loc] = array[loc]
                nanLoc = np.logical_or(outArray <= valueRange[0], outArray > valueRange[1])
                outArray[nanLoc] = bgValue

            # 3.min
            elif mode.upper() == "MIN":
                outArray = np.ones((height, width), dtype=np.float32) * (valueRange[1] + 1)
                for f in inputFileList:
                    warpDs = GdalUtil.raster_warp(f, "", extentInfo, resInfo, mode="MEM")
                    array = warpDs.GetRasterBand(1).ReadAsArray()
                    array = array.astype(np.float32)
                    nanLoc = np.logical_or(array <= valueRange[0], array > valueRange[1])
                    array[nanLoc] = np.nan
                    loc = array < outArray
                    outArray[loc] = array[loc]
                nanLoc = np.logical_or(outArray <= valueRange[0], outArray > valueRange[1])
                outArray[nanLoc] = bgValue
            else:
                print("Cannot calculate with mode :" + mode)

            outTifObj = GeoTiffFile(outputPath)
            outTifObj.setDims(width, height, 1)
            outTifObj.setGeoTrans(trans)
            outTifObj.setProj(proj)
            outTifObj.setData(outArray)
            outTifObj.writeTif()

        except Exception as e:
            return None

    @staticmethod
    def raster_warp(in_path, out_path, extent, res, nodata_val=-9999, mode="GTiff"):
        """
        统一栅格数据的经纬度、分辨率
        :param in_path: str 输入文件路径
        :param out_path: str 输出文件路径 若返回模式为MEM，outputPath可以设为""
        :param extent: dict  经纬度范围 {"xMin": lonMin, "xMax": lonMax, "yMin": latMin, "yMax": latMax}
        :param res: float 输出分辨率
        :param nodata_val: float 背景值
        :param mode: str 返回模式 "GTiff"-以tif形式存储到硬盘 "MEM"-存储在内存中
        :return:
        """
        out_bounds = (extent["xMin"], extent["yMin"], extent["xMax"], extent["yMax"])

        if mode.upper() == "GTIFF":
            ds = gdal.Warp(out_path, in_path, format='GTiff', outputBounds=out_bounds, dstNodata=nodata_val,
                           xRes=res, yRes=res)
        elif mode.upper() == "MEM":
            out_path = ""
            ds = gdal.Warp(out_path, in_path, format='MEM', outputBounds=out_bounds, dstNodata=nodata_val,
                           xRes=res, yRes=res)
        else:
            return None
        return ds

    @staticmethod
    def project(input_path, output_path, prj_info):
        """
        矢量/栅格重投影
        :param input_path: str: 输入文件路径
        :param output_path: str: 输出文件路径
        :param prj_info: str: 重投影信息 可使用三种形式：
                        type1 投影编码 : "EPSG:4326", "EPSG:4490"
                        type2 prj文件路径 : "./GCS_WGS_1984.prj"
                        type3 投影信息字符串 : 'GEOGCS["GCS_WGS_1984",
                                              DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],
                                              PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        :return:
        """
        if not BaseUtil.is_file(input_path):
            print("InputFile Error: ", input_path)
            return

        # 判断输入文件类型(栅格/矢量)
        ext = BaseUtil.file_ext(input_path)
        # 栅格
        if ext.upper() in [".TIF", ".TIFF"]:
            gdal.Warp(output_path, input_path, dstSRS=prj_info)
        # 矢量
        elif ext.upper() in [".SHP"]:
            gdal.VectorTranslate(output_path, input_path, dstSRS=prj_info, reproject=True)
        else:
            return

    @staticmethod
    def shp_rasterize(in_path, out_path, xres, yres, field_name, out_bounds=None, nodataValue=65535):
        """
        矢量文件栅格化

        :param in_path: str: 输入矢量文件路径
        :param out_path: str: 输出栅格文件路径
        :param xres: float: x向分辨率
        :param yres: float: y向分辨率
        :param field_name: str: 栅格化字段
        :return:
        """
        try:
            shp_obj = ShapeFile(in_path)
            shp_obj.readShp()
            if not out_bounds:
                shp_extend = shp_obj.getExtent()
                out_bounds = (shp_extend["xMin"], shp_extend["yMin"], shp_extend["xMax"], shp_extend["yMax"])

            # outputBounds [xmin, ymin, xmax, ymax]
            options = gdal.RasterizeOptions(outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=nodataValue,
                                            attribute=field_name, useZ=False, xRes=xres, yRes=yres, format="GTiff")
            ds = gdal.Rasterize(out_path, in_path, options=options)

            if not ds:
                return False
            del ds
            return True

        except Exception as e:
            print(e)
            return False

    @staticmethod
    def raster_clip_by_shp(in_path, out_path, shp_path, nodata_val=-9999):
        """
        依据shp边界对栅格数据进行裁切，输出TIF投影和输入TIF投影一致

        :param in_path: str: 栅格文件路径
        :param out_path: str: 输出栅格文件路径
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
            xres = tif_obj.getXRes()     # 获取栅格分辨率
            yres = tif_obj.getYRes()

            out_bounds = (shp_extend["xMin"], shp_extend["yMin"], shp_extend["xMax"], shp_extend["yMax"])
            # 方案1：裁切结果与shp左、上相切，强制分辨率与原始保持一致
            ds = gdal.Warp(out_path, in_path, format='GTiff', outputBounds=out_bounds, dstNodata=nodata_val,
                           cutlineDSName=shp_path, cropToCutline=False, xRes=xres, yRes=yres)

            # 方案2：裁切结果不会偏移，取shp内部像元，分辨率不变
            # ds = gdal.Warp(out_path, in_path, format='GTiff', outputBounds=out_bounds, dstNodata=nodata_val,
            #                cutlineDSName=shp_path, cropToCutline=True)

            if not ds:
                return False
            del ds
            return True

        except Exception as e:
            print(e)
            return False

    @staticmethod
    def grid(in_path, out_path, res, field_name, extend=None):
        """
        矢量文件插值为栅格   TODO 能否不生成.vrt文件

        :param in_path: str 输入矢量文件路径
        :param out_path: str 输出栅格文件路径
        :param res: float 输出栅格分辨率，单位：度
        :param field_name: str 被插值的属性字段
        :param extend: tuple 输出栅格范围 (ulx, uly, lrx, lry)
        :return:
        """

        # shp生成csv
        tempPath = BaseUtil.file_path_info(in_path)[0]
        baseName = BaseUtil.file_path_info(in_path)[1]
        csvName = baseName + ".csv"
        csvPath = os.path.join(tempPath, csvName)
        ShapeUtil.pointToCsv(in_path, csvPath, field_name)

        # 生成vrt
        vrtName = baseName + ".vrt"
        vrtPath = os.path.join(tempPath, vrtName)
        dom = XmlUtil.createDom()
        roodNode = XmlUtil.createRootNode(dom, "OGRVRTDataSource")
        OGRVRTLayerNode = XmlUtil.appendNode(dom, roodNode, "OGRVRTLayer", attrInfo={"name": baseName})
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "SrcDataSource", text=csvPath)
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "GeometryType", text="wkbPoint")
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "GeometryField",
                           attrInfo={"encoding": "PointFromColumns", "x": "field_1", "y": "field_2", "z": "field_3"})
        XmlUtil.saveDom(dom, vrtPath)

        # 计算输出范围
        if extend:
            xMin = extend[0]
            xMax = extend[2]
            yMin = extend[3]
            yMax = extend[1]
            outputBounds = extend
            width = int((xMax - xMin) / res)
            height = int((yMax - yMin) / res)
        else:
            csvData = pd.read_csv(csvPath, header=None)
            xMin = csvData[0].min()
            xMax = csvData[0].max()
            yMin = csvData[1].min()
            yMax = csvData[1].max()
            outputBounds = (xMin, yMax, xMax, yMin)
            width = int((xMax - xMin) / res)
            height = int((yMax - yMin) / res)

        # .prj文件
        prjFile = os.path.join(BaseUtil.file_path_info(in_path)[0], BaseUtil.file_path_info(in_path)[1] + ".prj")

        # 插值算法参数
        algo = 'invdist:power=2.0:smoothing=0.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0'
        options = gdal.GridOptions(outputType=gdal.GDT_Float32, outputBounds=outputBounds, layers=baseName,
                                   format='GTiff', algorithm=algo, width=width, height=height, outputSRS=prjFile)
        gdal.Grid(out_path, vrtPath, options=options)

    @staticmethod
    def gridByTxt(inputPath, outputPath, prjFile, cellSize, extend=None):
        """
        txt文件插值为栅格  TODO 统一输入输出文件规范

        :param inputPath: str 输入txt文件路径
        :param outputPath: str 输出栅格文件路径
        :param cellSize: float 输出栅格分辨率，单位：度
        :param extend: tuple 输出栅格范围 (ulx, uly, lrx, lry)
        :return:
        """

        # shp生成csv
        tempPath = BaseUtil.file_path_info(inputPath)[0]
        baseName = BaseUtil.file_path_info(inputPath)[1]
        # csvName = baseName + ".csv"
        # csvPath = os.path.join(tempPath, csvName)
        # ShapeUtil.pointToCsv(inputPath, csvPath, zField)

        # 生成vrt
        vrtName = baseName + ".vrt"
        vrtPath = os.path.join(tempPath, vrtName)
        dom = XmlUtil.createDom()
        roodNode = XmlUtil.createRootNode(dom, "OGRVRTDataSource")
        OGRVRTLayerNode = XmlUtil.appendNode(dom, roodNode, "OGRVRTLayer", attrInfo={"name": baseName})
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "SrcDataSource", text=inputPath)
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "GeometryType", text="wkbPoint")
        XmlUtil.appendNode(dom, OGRVRTLayerNode, "GeometryField",
                           attrInfo={"encoding": "PointFromColumns", "x": "field_1", "y": "field_2", "z": "field_3"})
        XmlUtil.saveDom(dom, vrtPath)

        # 计算输出范围
        if extend:
            xMin = extend[0]
            xMax = extend[2]
            yMin = extend[3]
            yMax = extend[1]
            outputBounds = extend
            width = int((xMax - xMin) / cellSize)
            height = int((yMax - yMin) / cellSize)
        else:
            csvData = pd.read_csv(inputPath, header=None, sep=" ")
            xMin = csvData[0].min()
            xMax = csvData[0].max()
            yMin = csvData[1].min()
            yMax = csvData[1].max()
            outputBounds = (xMin, yMax, xMax, yMin)
            width = int((xMax - xMin) / cellSize)
            height = int((yMax - yMin) / cellSize)

        # 插值算法参数
        algo = 'invdist:power=2.0:smoothing=0.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0'
        options = gdal.GridOptions(outputType=gdal.GDT_Float32, outputBounds=outputBounds, layers=baseName,
                                   format='GTiff', algorithm=algo, width=width, height=height, outputSRS=prjFile)
        gdal.Grid(outputPath, vrtPath, options=options)

    @staticmethod
    def rasterClipByCondition(tifPath, shpPath, outTifPath, condition):
        """根据属性表条件进行裁切"""
        ds = gdal.Warp(outTifPath, tifPath, format='GTiff', cutlineDSName=shpPath, dstNodata=-9999,
                       cutlineWhere=condition)  # 属性表筛选条件
        # eg:
        # cutlineWhere = "ID = '530100000000'"

        # options --- 字符串数组, 字符串或者空值
        # format --- 输出格式 ("GTiff", etc...)
        # outputBounds --- 结果在目标空间参考的边界范围(minX, minY, maxX, maxY)
        # outputBoundsSRS --- 结果边界范围的空间参考, 如果在dstSRS中没有指定的话，采用此参数
        # xRes, yRes --- 输出分辨率，即像素的大小
        # targetAlignedPixels --- 是否强制输出边界是输出分辨率的倍数
        # width --- 输出栅格的列数
        # height --- 输出栅格的行数
        # srcSRS --- 输入数据集的空间参考
        # dstSRS --- 输出数据集的空间参考
        # srcAlpha --- 是否将输入数据集的最后一个波段作为alpha波段
        # dstAlpha --- 是否强制创建输出
        # outputType --- 输出栅格的变量类型 (gdal.GDT_Byte, etc...)
        # workingType --- working type (gdal.GDT_Byte, etc...)
        # warpOptions --- list of warping options
        # errorThreshold --- 近似转换的误差阈值(误差像素数目)
        # warpMemoryLimit --- 工作内存限制 Bytes
        # resampleAlg --- 重采样方法
        # creationOptions --- list of creation options
        # srcNodata --- 输入栅格的无效值
        # dstNodata --- 输出栅格的无效值
        # multithread --- 是否多线程和I/O操作
        # tps --- 是否使用Thin Plate Spline校正方法
        # rpc --- 是否使用RPC校正
        # geoloc --- 是否使用地理查找表校正
        # polynomialOrder --- 几何多项式校正次数
        # transformerOptions --- list of transformer options
        # cutlineDSName --- cutline数据集名称
        # cutlineLayer --- cutline图层名称
        # cutlineWhere --- cutline WHERE 子句
        # cutlineSQL --- cutline SQL语句
        # cutlineBlend --- cutline blend distance in pixels
        # cropToCutline --- 是否使用切割线范围作为输出边界
        # copyMetadata --- 是否复制元数据
        # metadataConflictValue --- 元数据冲突值
        # setColorInterpretation --- 是否强制将输入栅格颜色表给输出栅格
        # callback --- 回调函数
        # callback_data --- 用于回调的用户数据

    @staticmethod
    def getSRSPair(dataset):
        '''
        获得给定数据的投影参考系和地理参考系
        :param dataset: GDAL地理数据
        :return: 投影参考系和地理参考系
        '''
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(dataset.GetProjection())
        geosrs = prosrs.CloneGeogCS()
        return prosrs, geosrs

    @staticmethod
    def geo2lonlat(dataset, x, y):
        '''
        将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
        :param dataset: GDAL地理数据
        :param x: 投影坐标x
        :param y: 投影坐标y
        :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
        '''
        prosrs, geosrs = GdalUtil.getSRSPair(dataset)
        ct = osr.CoordinateTransformation(prosrs, geosrs)
        coords = ct.TransformPoint(x, y)
        return coords[:2]

    @staticmethod
    def imagexy2geo(dataset, row, col):
        '''
        根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
        :param dataset: GDAL地理数据
        :param row: 像素的行号
        :param col: 像素的列号
        :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
        '''
        trans = dataset.GetGeoTransform()
        px = trans[0] + col * trans[1] + row * trans[2]
        py = trans[3] + col * trans[4] + row * trans[5]
        return px, py

    @staticmethod
    def read_tif(inputfile, band):
        tifObj = GeoTiffFile(inputfile)
        tifObj.readTif()
        data = tifObj.getBandData(band)
        width = tifObj.getWidth()
        height = tifObj.getHeight()
        proj = tifObj.getProj()
        geotrans = tifObj.getGeoTrans()
        return data, width, height, proj, geotrans

    @staticmethod
    def write_tif(data, band, width, height, proj, geotrans, outpath):
        outTifObj = GeoTiffFile(outpath)
        outTifObj.setDims(width, height, band)
        outTifObj.setProj(proj)
        outTifObj.setGeoTrans(geotrans)
        outTifObj.setData(data)
        outTifObj.writeTif()

    @staticmethod
    def shp_project(input_path, output_path, prj_info):
        """
        矢量重投影
        TODO 不可用 有问题
        """
        os.environ['SHAPE_ENCODING'] = "utf-8"

        src_file = input_path
        dst_file = output_path

        src_ds = ogr.Open(src_file)
        src_layer = src_ds.GetLayer(0)
        src_srs = src_layer.GetSpatialRef()  # 读取输入数据投影

        # 输出数据投影定义，参考资料：http://spatialreference.org/ref/sr-org/8657
        # srs_def = """+proj=aea +lat_1=25 +lat_2=47 +lat_0=30 +lon_0=105 +x_0=0 +y_0=0
        # +ellps=WGS84 +datum=WGS84 +units=m +no_defs """
        dst_srs = osr.SpatialReference()  # 创建输出数据投影
        dst_srs.ImportFromEPSG(prj_info)  # 定义输出数据投影
        ctx = osr.CoordinateTransformation(src_srs, dst_srs)  # 投影创建转换对象

        # 创建输出文件
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dst_ds = driver.CreateDataSource(dst_file)
        dst_layer = dst_ds.CreateLayer('temp', dst_srs, ogr.wkbPolygon)

        # 给输出文件图层添加属性定义
        layer_def = src_layer.GetLayerDefn()
        for i in range(layer_def.GetFieldCount()):
            field_def = layer_def.GetFieldDefn(i)
            dst_layer.CreateField(field_def)

        # 循环遍历源Shapefile中的几何体添加到目标文件中
        src_feature = src_layer.GetNextFeature()
        while src_feature:
            geometry = src_feature.GetGeometryRef()
            geometry.Transform(ctx)
            dst_feature = ogr.Feature(layer_def)
            dst_feature.SetGeometry(geometry)  # 设置Geometry
            # 依次设置属性值
            for i in range(layer_def.GetFieldCount()):
                field_def = layer_def.GetFieldDefn(i)
                field_name = field_def.GetName()
                dst_feature.SetField(field_name, src_feature.GetField(field_name))
            dst_layer.CreateFeature(dst_feature)
            del dst_feature
            del src_feature
            src_feature = src_layer.GetNextFeature()
        dst_ds.FlushCache()

        del src_ds
        del dst_ds

    @staticmethod
    def raster_project(in_path, out_path, prj_info):
        """
        根据指定投影信息对栅格数据进行投影转换（支持投影编码，投影字符串等形式）

        :param in_path: str: 输入栅格文件路径
        :param out_path: str: 输出栅格文件路径
        :param prj_info: str: 投影文件路径 e.g:
                        type1 投影编码 : "EPSG:4326", "EPSG:4490"
                        type2 prj文件路径 : "./GCS_WGS_1984.prj"
                        type3 投影信息字符串 : 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
        :return:
        """
        try:
            ds = gdal.Warp(out_path, in_path, dstSRS=prj_info)
            if not ds:
                return False
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    inFile = r'C:\Users\Administrator\Desktop\model\input\satellite\Sentinel3-OLCI-300\Sentinel3B_OLCI_L2_202010300952_300_0180_045_Clip.tif'
    ds = gdal.Open(inFile)
    width = ds.RasterXSize
    height = ds.RasterYSize
    bands = ds.RasterCount
    proj = ds.GetProjection()
    geoTrans = ds.GetGeoTransform()

    outFile = r'C:\Users\Administrator\Desktop\model\input\satellite\Sentinel3-OLCI-300\a.tif'
    driver = gdal.GetDriverByName("GTiff")
    outds = driver.Create(outFile, width, height, bands, gdal.GDT_Float32)
    outds.SetGeoTransform(geoTrans)
    outds.SetProjection(proj)

    for i in range(bands):
        data = ds.GetRasterBand(i+1).ReadAsArray()
        data[data < -1] = 65535
        outds.GetRasterBand(i+1).WriteArray(data)
    outds = None
    print('Finish')