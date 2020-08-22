# -*- coding: utf-8 -*-
# @Time : 2020/8/10 9:32
# @Author : wangbin

import gdal
from TimeUtil import TimeUtil

if __name__ == '__main__':
    # 1.年日转月日
    issue = "2019-229"
    a = TimeUtil.str_to_datetime(issue, "%Y-%j")
    b = TimeUtil.datetime_to_str(a, "%Y-%m-%d")
    print(b)

    in_path = r'F:\zktq\data\original\MODIS\TERRA_X_2020_07_25_10_26_D_G.MOD02QKM.hdf'

    ds = gdal.Open(in_path)
    sub_ds = ds.GetSubDatasets()
    target_ds = list(filter(lambda x: 'EV_250_RefSB' in str(x), sub_ds))
    target_list = []
    target_index = sub_ds.index(target_ds[0])
    target_list.append(sub_ds[target_index][0])

    out_path = r'C:\Users\Think\Desktop\output\out.tif'
    # warpMemoryLimit=1*1024*1024*1024*6
    gdal.Warp(out_path, target_list[0], dstSRS='EPSG:4326', format='GTiff')
    print('Finish')

