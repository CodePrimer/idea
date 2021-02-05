from pyhdf.SD import SD, SDC
import h5py
import os
import numpy as np
from GeoTiffFile import GeoTiffFile
from GdalUtil import GdalUtil


def merge_hdf(input_file, temp_dir, file_basename):
    """
    合并h5文件 以便后续做地理校正
    @param input_file: 输入svi01数据路径
    @param temp_dir: 临时文件夹
    @return: hdf_path: 合并后的hdf文件路径
    """
    # 输出合并结果hdf文件
    merge_hdf_path = os.path.join(temp_dir, file_basename + '_merge.hdf')
    merge_info = {"svi01": (input_file, 'All_Data/VIIRS-I1-SDR_All/Radiance'),
                  "svi02": (input_file.replace("svi01.h5", "svi02.h5"), 'All_Data/VIIRS-I2-SDR_All/Radiance'),
                  "svi03": (input_file.replace("svi01.h5", "svi03.h5"), 'All_Data/VIIRS-I3-SDR_All/Radiance'),
                  "svi04": (input_file.replace("svi01.h5", "svi04.h5"), 'All_Data/VIIRS-I4-SDR_All/Radiance'),
                  "SatelliteAzimuthAngle": (
                  input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/SatelliteAzimuthAngle'),
                  "SatelliteZenithAngle": (
                  input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/SatelliteZenithAngle'),
                  "SolarAzimuthAngle": (
                  input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/SolarAzimuthAngle'),
                  "SolarZenithAngle": (
                  input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/SolarZenithAngle'),
                  "Latitude": (input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Latitude'),
                  "Longitude": (input_file.replace("svi01.h5", "gimgo.h5"), 'All_Data/VIIRS-IMG-GEO_All/Longitude')}

    # 创建输出hdf对象
    merge_sd = SD(merge_hdf_path, SDC.CREATE | SDC.WRITE)
    merge_list = ['svi01', 'svi02', 'svi03', 'svi04', 'SatelliteAzimuthAngle', 'SatelliteZenithAngle',
                  'SolarAzimuthAngle', 'SolarZenithAngle', 'Latitude', 'Longitude']
    for i in range(len(merge_list)):
        cur_file_path = merge_info[merge_list[i]][0]
        cur_h5_file = h5py.File(cur_file_path, 'r')
        # 获取数组
        cur_ds = cur_h5_file[merge_info[merge_list[i]][1]]
        cur_data = np.array(cur_ds)
        # 创建hdf中数据集create(数据集名称, 数据类型, 数据大小)
        if merge_list[i] in ['Latitude', 'Longitude', 'SatelliteAzimuthAngle', 'SatelliteZenithAngle',
                             'SolarAzimuthAngle', 'SolarZenithAngle']:
            cur_sd_obj = merge_sd.create(merge_list[i], SDC.FLOAT32, (cur_data.shape[0], cur_data.shape[1]))
        else:
            cur_sd_obj = merge_sd.create(merge_list[i], SDC.UINT16, (cur_data.shape[0], cur_data.shape[1]))
        # 设置数据集数据 传入numpy数组
        cur_sd_obj.set(cur_data)
        cur_sd_obj.endaccess()
    merge_sd.end()
    return merge_hdf_path


def gdal_geo_warp(merge_hdf, temp_dir):
    gdal_warp_path = r'D:\Miniconda3\envs\jiangsu_water_demo_model\Library\bin\gdalwarp.exe'
    warp_list = ['svi01', 'svi02', 'svi03', 'svi04', 'SatelliteAzimuthAngle', 'SatelliteZenithAngle',
                 'SolarAzimuthAngle', 'SolarZenithAngle']
    out_file_path = {}
    for i in range(len(warp_list)):
        out_geo_file_name = os.path.basename(merge_hdf).replace('merge.hdf', warp_list[i] + '_proj.tif')
        out_geo_file_path = os.path.join(temp_dir, out_geo_file_name)
        param_str = '-geoloc -t_srs EPSG:4326 -srcnodata 65533 HDF4_SDS:UNKNOWN:"%s":%s %s' % \
                    (merge_hdf, i, out_geo_file_path)
        cmd_str = gdal_warp_path + ' ' + param_str
        os.system(cmd_str)
        out_file_path[warp_list[i]] = out_geo_file_path
    return out_file_path


def get_sixs_param(warp_path, temp_dir, file_basename):

    sixs_exe_path = r'C:\6S\6s.exe'
    in_txt_path = os.path.join(os.path.dirname(sixs_exe_path), 'in.txt')
    angle = {'SolarZenithAngle': None, 'SolarAzimuthAngle': None,
             'SatelliteZenithAngle': None, 'SatelliteAzimuthAngle': None}
    extent = {'xMin': 119.89, 'xMax': 120.64, 'yMin': 30.93, 'yMax': 31.55}
    for each in angle.keys():
        clip_tif_path = os.path.join(temp_dir, os.path.basename(warp_path[each]).replace('.tif', '_clip.tif'))
        GdalUtil.raster_warp(warp_path[each], clip_tif_path, extent, 0.004667, nodata_val=65533)
        tif_obj = GeoTiffFile(clip_tif_path)
        tif_obj.readTif()
        extent = tif_obj.getGeoExtent()
        data_array = tif_obj.getBandData(0)
        data_array[data_array == 65533] = np.nan
        angle_mean = abs(float(np.nanmean(data_array)))
        angle[each] = angle_mean

    # 月 日
    month = int(file_basename.split('_')[2][5:7])
    day = int(file_basename.split('_')[2][7:9])
    # 大气模式
    center_lat = (extent['yMax'] + extent['yMin']) / 2
    if center_lat < 23.5 and month < 9 and month > 2:
        atmo_model = 1
    elif center_lat >= 23.5 and center_lat < 66.5 and month < 9 and month > 2:
        atmo_model = 2
    elif center_lat >= 23.5 and center_lat < 66.5 and (month >= 9 or month <= 2):
        atmo_model = 3
    elif center_lat >= 66.5 and month < 9 and month > 2:
        atmo_model = 4
    elif center_lat >= 66.5 and (month >= 9 or month <= 2):
        atmo_model = 5
    else:
        # 错误
        atmo_model = 0

    # 波长范围
    wave_range = {'svi01': (0.6025, 0.6775),
                  'svi02': (0.8455, 0.8845),
                  'svi03': (1.58, 1.64),
                  'svi04': (3.55, 3.93)}
    atmo_param = {'svi01': None, 'svi02': None, 'svi03': None, 'svi04': None}
    for each in atmo_param.keys():
        # 写入in.txt
        with open(in_txt_path, 'w') as f:
            f.write('%d\n' % 0)     # 自定义几何
            f.write('%.2f\n' % angle['SolarZenithAngle'])   # 太阳天顶角
            f.write('%.2f\n' % angle['SolarAzimuthAngle'])  # 太阳方位角
            f.write('%.2f\n' % angle['SatelliteZenithAngle'])  # 卫星天顶角
            f.write('%.2f\n' % angle['SatelliteAzimuthAngle'])  # 卫星方位角
            f.write('%d\n' % month)     # 月
            f.write('%d\n' % day)       # 日
            f.write('%d\n' % atmo_model)    # 大气模式
            f.write('%d\n' % 1)      # 气溶胶类型
            f.write('%.1f\n' % 15.0)           # 气溶胶参数
            f.write('%.3f\n' % -0.010)        # 目标高度
            f.write('%d\n' % -1000)   # 传感器高度
            f.write('%d\n' % 0)    # 自定义输入波长
            f.write('%.4f\n' % wave_range[each][0])    # 波长起始
            f.write('%.4f\n' % wave_range[each][1])    # 波长终止
            f.write('%d\n' % 0)           # 无方向反射
            f.write('%d\n' % 0)       # 朗伯体假设
            f.write('%d\n' % 4)         # 湖泊水体
            f.write('%.1f\n' % -0.4)     # 进行大气校正

        sixs_exe_dir = os.path.dirname(sixs_exe_path)
        sixs_exe_name = os.path.basename(sixs_exe_path)
        cmd_str = 'cd %s && %s<%s>log.txt' % (sixs_exe_dir, sixs_exe_name, 'in.txt')
        os.system(cmd_str)
        sixs_out_path = os.path.join(sixs_exe_dir, 'sixs.out')
        with open(sixs_out_path, 'r') as f1:
            line_str = f1.readline()
            while line_str:
                line_str = f1.readline()
                # print(line_str)
                if 'coefficients xa xb xc' in line_str:
                    atmo_param_str = line_str.split(':')[1]
                    xa = float(atmo_param_str.split('   ')[1])
                    xb = float(atmo_param_str.split('   ')[2])
                    xc = float(atmo_param_str.split('   ')[3])
                    print(xa, xb, xc)
                    atmo_param[each] = (xa, xb, xc)
    return atmo_param


def cal_radiance(warp_path, atmo_param, out_tif_path):
    radiance_factor = {'svi01': (0.013155036, -0.41), 'svi02': (0.0063949213, -0.24),
                       'svi03': (0.0013309018, -0.21), 'svi04': (5.52444e-05, -0.01)}

    # 先获取行列号
    tif_path = warp_path['svi01']
    tif_obj = GeoTiffFile(tif_path)
    tif_obj.readTif()
    width = tif_obj.getWidth()
    height = tif_obj.getHeight()
    proj = tif_obj.getProj()
    geo_trans = tif_obj.getGeoTrans()
    del tif_obj

    out_tif_obj = GeoTiffFile(out_tif_path)
    out_tif_data = np.zeros((4, height, width), dtype=np.float)
    i = 0
    for key in radiance_factor.keys():
        tif_path = warp_path[key]
        tif_obj = GeoTiffFile(tif_path)
        tif_obj.readTif()
        tif_data = tif_obj.getBandData(0)
        nan_loc = tif_data >= 65530
        # 辐射定标计算
        tif_data = tif_data * radiance_factor[key][0] + radiance_factor[key][1]
        # 大气校正计算
        # y=xa*(measured radiance)-xb;  acr=y/(1.+xc*y)
        y = atmo_param[key][0] * tif_data - atmo_param[key][1]
        ref_data = y / (1 + atmo_param[key][2] * y) * 1000
        # ref_data = ref_data.astype(np.uint16)
        ref_data[nan_loc] = 65533
        out_tif_data[i, :, :] = ref_data
        i += 1
    out_tif_obj.setDims(width, height, 4)
    out_tif_obj.setData(out_tif_data)
    out_tif_obj.setProj(proj)
    out_tif_obj.setGeoTrans(geo_trans)
    out_tif_obj.writeTif()

    print("finish")


if __name__ == '__main__':

    input_path = r'F:\zktq\data\original\NPP\202007021241\RNSCA-RVIRS_npp_d20200702_t1241_svi01.h5'
    temp_dir = r'C:\Users\Administrator\Desktop\temp'

    basename = os.path.basename(input_path).replace('_svi01.h5', '')

    # 合并h5数据集
    hdf_path = merge_hdf(input_path, temp_dir, basename)
    # 地理校正
    warp_path = gdal_geo_warp(hdf_path, temp_dir)

    # 获取大气校正参数
    atmo_param = get_sixs_param(warp_path, temp_dir, basename)
    # 辐射定标 大气校正
    out_tif_path = os.path.join(r'E:\NPP', basename + '_reproj.tif')
    cal_radiance(warp_path, atmo_param, out_tif_path)

    print("finish")