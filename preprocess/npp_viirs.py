# -*- coding: utf-8  -*-
# -*- author: wangbin -*-

import os
import gdal
import h5py
import numpy as np
import osr
from BaseUtil import BaseUtil
from GeoTiffFile import GeoTiffFile

def delete():
    pass
    # geo_h5_file = r'E:\NPP\ori\20200704\1344\RNSCA-RVIRS_npp_d20200704_t1344_gimgo.h5'
    # if not BaseUtil.is_file(geo_h5_file):
    #     print("FileNotFound.")
    # h5_ds = gdal.Open(geo_h5_file)
    #
    # # 生成经纬度栅格数据
    # # Latitude
    # ds_path = get_dataset_path(h5_ds, "Latitude")
    # ds = gdal.Open(ds_path)
    # data = ds.GetRasterBand(1).ReadAsArray()
    # out_lat = r'E:\NPP\temp\Latitude.tif'
    # write_tif(out_lat, data, gdal.GDT_Float32)
    #
    # # Longitude
    # ds_path = get_dataset_path(h5_ds, "Longitude")
    # ds = gdal.Open(ds_path)
    # data = ds.GetRasterBand(1).ReadAsArray()
    # out_lon = r'E:\NPP\temp\Longitude.tif'
    # write_tif(out_lon, data, gdal.GDT_Float32)
    #
    # svi01_h5_file = r'E:\NPP\ori\20200704\1344\RNSCA-RVIRS_npp_d20200704_t1344_svi01.h5'
    # h5_ds = gdal.Open(svi01_h5_file)
    # ds_path = get_dataset_path(h5_ds, "Radiance")
    # ds = gdal.Open(ds_path)
    # data = ds.GetRasterBand(1).ReadAsArray()
    # out_lat = r'E:\NPP\temp\svi01.tif'
    # write_tif(out_lat, data, gdal.GDT_UInt16)

    # # 地理校正
    # vrt_path = r'E:\NPP\temp\test.vrt'
    # out_path = r'E:\NPP\temp\out.tif'
    # gdal.Warp(out_path, vrt_path, geoloc=True)


def delete2():
    nbands = 4
    mask_value = 65533
    # input_path: 输入svi01文件路径
    # output_path: 输出tif文件路径
    input_path = r'E:\NPP\ori\20200704\1344\RNSCA-RVIRS_npp_d20200704_t1344_svi01.h5'

    merge_info = {"svi01": (input_path, 'All_Data/VIIRS-I1-SDR_All/Radiance'),
                  "svi02": (input_path.replace("svi01.h5", "svi02.h5"), 'All_Data/VIIRS-I2-SDR_All/Radiance'),
                  "svi03": (input_path.replace("svi01.h5", "svi03.h5"), 'All_Data/VIIRS-I3-SDR_All/Radiance'),
                  "svi04": (input_path.replace("svi01.h5", "svi04.h5"), 'All_Data/VIIRS-I4-SDR_All/Radiance'),
                  "Latitude": (input_path.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Latitude'),
                  "Longitude": (input_path.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Longitude')}

    out_merge_path = input_path.replace('_svi01.h5', '_merge.hdf')
    out_merge_file = h5py.File(out_merge_path, 'w')
    radiance_factor = {}
    for key in merge_info.keys():
        cur_file_path = merge_info[key][0]
        cur_h5_file = h5py.File(cur_file_path, 'r')
        # 获取数组
        cur_ds = cur_h5_file[merge_info[key][1]]
        cur_data = np.array(cur_ds)
        if key not in ['Latitude', 'Longitude']:
            cur_factor = np.array(cur_h5_file[merge_info[key][1]+'Factors'])
            gain = cur_factor[0]
            bias = cur_factor[1]
            radiance_factor[key] = (gain, bias)
            print(gain)
            print(bias)
        out_merge_file[key] = cur_data
    out_merge_file.close()
    out_geo_tif = 'E:/NPP/temp/svi01.tif'

    ds = gdal.Open(out_merge_path)
    abc = get_dataset_path(ds, 'svi01')
    warp_option = gdal.WarpOptions(xRes=0.0037, yRes=0.0037, dstSRS="EPSG:4326", format='GTiff', geoloc=True)
    gdal.Warp(out_geo_tif, abc, options=warp_option)

    # '-geoloc -t_srs EPSG:4326 -srcnodata 65533 HDF5:"E:/NPP/temp/RNSCA-RVIRS_npp_d20200704_t1344_merge.hdf"://svi01 E:/NPP/temp/RNSCA-RVIRS_npp_d20200704_t1344_merge.hdf'


def delete3():
    pass
    tif_path1 = r'E:\NPP\temp\svi01.tif'
    lat_path = r'E:\NPP\temp\Latitude.tif'
    lon_path = r'E:\NPP\temp\Longitude.tif'
    tif_obj1 = GeoTiffFile(lat_path)
    tif_obj1.readTif()
    lat_data = tif_obj1.getBandData(0)
    tif_obj2 = GeoTiffFile(lon_path)
    tif_obj2.readTif()
    lon_data = tif_obj2.getBandData(0)
    dataset = gdal.Open(tif_path1, gdal.GA_Update)
    geo_line = 7680     # 地理信息行数
    geo_sample = 6400   # 地理信息列数

    # 采样间隔
    resample_step = 100
    resample_line_num = int(geo_line / resample_step)
    resample_sample_num = int(geo_sample / resample_step)
    position_list = []
    for i in range(resample_line_num):
        for j in range(resample_sample_num):
            position_list.append(((i+1) * resample_step - 1, (j+1) * resample_step - 1))
    gcps_list = []
    for each in position_list:
        lie = each[1]
        hang = each[0]
        lon = float(lon_data[hang][lie])
        lat = float(lat_data[hang][lie])
        gdal_gcp = gdal.GCP(lon, lat, 0, lie, hang)
        gcps_list.append(gdal_gcp)
    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS('WGS84')
    # 添加控制点
    dataset.SetGCPs(gcps_list, sr.ExportToWkt())

    out_tif_path = r'E:\NPP\temp\svi01_proj.tif.'
    dst_ds = gdal.Warp(out_tif_path, dataset, format='GTiff', tps=True, xRes=0.0037, yRes=0.0037, dstNodata=65533,
                       resampleAlg=gdal.GRIORA_NearestNeighbour, outputType=gdal.GDT_UInt16)

    """
    # gdal.GCP([x], [y], [z], [pixel], [line], [info], [id])
    # x、y、z是控制点对应的投影坐标，默认为0;
    # pixel、line是控制点在图像上的列、行位置，默认为0;
    # info、id是用于说明控制点的描述和点号的可选字符串，默认为空.
    """


def get_dataset_path(hdf_ds, target_ds_name):
    """
    获取子数据集的路径信息
    @param hdf_ds: gdal打开的hdf文件数据集对象
    @param target_ds_name: 搜索数据集名称
    @return: path: 子数据集路径
    """

    if not isinstance(hdf_ds, gdal.Dataset) or not isinstance(target_ds_name, str):
        print("输入数据类型错误")
    path = None    # 保证搜索不到时返回None
    sub_ds_list = hdf_ds.GetSubDatasets()
    for each in sub_ds_list:
        sub_ds_info = each[0]
        sub_ds_path = sub_ds_info.split(":")[-1]  # TODO 会不会受windows盘符影像
        sub_ds_basename = os.path.basename(sub_ds_path)
        if target_ds_name == sub_ds_basename:
            path = each[0]
            break
    return path


def write_tif(out_path, data, data_type):
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(out_path, data.shape[1], data.shape[0], 1, data_type)
    out_ds.GetRasterBand(1).WriteArray(data)
    del out_ds


if __name__ == '__main__':

    # input_path = r'E:\NPP\ori\20200704\1344\RNSCA-RVIRS_npp_d20200704_t1344_svi01.h5'
    #
    # merge_info = {"svi01": (input_path, 'All_Data/VIIRS-I1-SDR_All/Radiance'),
    #               "svi02": (input_path.replace("svi01.h5", "svi02.h5"), 'All_Data/VIIRS-I2-SDR_All/Radiance'),
    #               "svi03": (input_path.replace("svi01.h5", "svi03.h5"), 'All_Data/VIIRS-I3-SDR_All/Radiance'),
    #               "svi04": (input_path.replace("svi01.h5", "svi04.h5"), 'All_Data/VIIRS-I4-SDR_All/Radiance'),
    #               "Latitude": (input_path.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Latitude'),
    #               "Longitude": (input_path.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Longitude')}
    #
    # radiance_factor = {'svi01': (0.013155036, -0.41), 'svi02': (0.0063949213, -0.24), 'svi03': (0.0013309018, -0.21), 'svi04': (5.52444e-05, -0.01)}
    # for key in merge_info.keys():
    #     cur_file_path = merge_info[key][0]
    #     cur_h5_file = h5py.File(cur_file_path, 'r')
    #     # 获取数组
    #     cur_ds = cur_h5_file[merge_info[key][1]]
    #     cur_data = np.array(cur_ds)
    #     cur_out_tif_path = os.path.join(r'E:\NPP\temp', key + '.tif')
    #     driver = gdal.GetDriverByName("GTiff")
    #     if key in ['Latitude', 'Longitude']:
    #         type = gdal.GDT_Float32
    #     else:
    #         type = gdal.GDT_UInt16
    #     cur_ds = driver.Create(cur_out_tif_path, cur_data.shape[1], cur_data.shape[0], 1, type)
    #     cur_ds.GetRasterBand(1).WriteArray(cur_data)
    #     del cur_ds



    print('Finish')
