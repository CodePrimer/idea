# -*- coding: utf-8 -*-
# @Time : 2020/8/9 19:46
# @Author : wangbin

import gdal


if __name__ == '__main__':
    in_path = r'C:\Users\Think\Desktop\input\MYD02QKM.A2019120.0425.061.2019120153722.hdf'

    ds = gdal.Open(in_path)
    sub_ds = ds.GetSubDatasets()
    target_ds = list(filter(lambda x: 'EV_250_RefSB' in str(x), sub_ds))
    target_list = []
    target_index = sub_ds.index(target_ds[0])
    target_list.append(sub_ds[target_index][0])

    out_path = r'C:\Users\Think\Desktop\output\out1.tif'
    gdal.Warp(out_path, target_list[0], dstSRS='EPSG:4326', format='GTiff')
    print('Finish')