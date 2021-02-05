# -*- coding: utf-8 -*-
# @Time : 2020/8/10 9:32
# @Author : wangbin

import gdal
import osr
from pyhdf.SD import SD,SDC,SDS

'''
生成vrt文件
gdal_translate -of VRT HDF4_EOS:EOS_SWATH:"C:/Users/Administrator/Desktop/hdf/TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf":MODIS_SWATH_Type_L1B:EV_250_RefSB C:/Users/Administrator/Desktop/hdf/vrt1.vrt
'''


def gcpTransform():
    in_path = r'C:\Users\Administrator\Desktop\hdf\TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf'
    hdfDs = gdal.Open(in_path)
    hdfSubDsList = hdfDs.GetSubDatasets()
    target_ds = list(filter(lambda x: 'EV_250_RefSB' in str(x), hdfSubDsList))
    target_list = []
    target_index = hdfSubDsList.index(target_ds[0])
    target_list.append(hdfSubDsList[target_index][0])
    refDs = gdal.Open(target_list[0])

    gcpList = refDs.GetGCPs()
    gcpNewList = []
    for each in gcpList:
        if each.GCPX != -999 and each.GCPY != -999:
            print(each.GCPX)
            print(each.GCPY)
            print(each.GCPLine)
            print(each.GCPPixel)
            gcpNewList.append(each)
    gcpNewTuple = tuple(gcpNewList)

    sr = osr.SpatialReference()
    sr.SetWellKnownGeogCS('WGS84')

    refTifPath = r'C:\Users\Administrator\Desktop\hdf\RefSB.tif'
    refTifDs = gdal.Open(refTifPath, gdal.GA_Update)
    refTifDs.SetGCPs(gcpNewTuple, sr.ExportToWkt())

    projTifPath = r'C:\Users\Administrator\Desktop\hdf\RefSB_proj.tif'
    dst_ds = gdal.Warp(projTifPath, refTifDs, format='GTiff', tps=True, dstNodata=65533,
                       resampleAlg=gdal.GRIORA_NearestNeighbour, outputType=gdal.GDT_UInt16)


def refSB():

    in_path = r'C:\Users\Administrator\Desktop\hdf\TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf'
    hdfDs = gdal.Open(in_path)
    hdfSubDsList = hdfDs.GetSubDatasets()
    target_ds = list(filter(lambda x: 'EV_250_RefSB' in str(x), hdfSubDsList))
    target_list = []
    target_index = hdfSubDsList.index(target_ds[0])
    target_list.append(hdfSubDsList[target_index][0])
    refDs = gdal.Open(target_list[0])

    bandArray1 = refDs.GetRasterBand(1).ReadAsArray()
    bandArray1 = bandArray1[0:9920, :]
    outBand1 = r'C:\Users\Administrator\Desktop\hdf\band1.tif'
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outBand1, bandArray1.shape[1], bandArray1.shape[0], 1, gdal.GDT_UInt16)
    ds.GetRasterBand(1).WriteArray(bandArray1)
    ds = None

    bandArray2 = refDs.GetRasterBand(2).ReadAsArray()
    bandArray2 = bandArray2[0:9920, :]
    outBand1 = r'C:\Users\Administrator\Desktop\hdf\band2.tif'
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outBand1, bandArray2.shape[1], bandArray2.shape[0], 1, gdal.GDT_UInt16)
    ds.GetRasterBand(1).WriteArray(bandArray2)
    ds = None

    print('a')
    # refTifPath = r'C:\Users\Administrator\Desktop\hdf\RefSB.tif'
    # driver = gdal.GetDriverByName("GTiff")
    # outRefDs = driver.Create(refTifPath, refDs.RasterXSize, refDs.RasterYSize, refDs.RasterCount, gdal.GDT_UInt16)
    #
    # outRefDs.GetRasterBand(1).WriteArray(bandArray1)
    # outRefDs = None

    """
    # gdal.GCP([x], [y], [z], [pixel], [line], [info], [id])
    # x、y、z是控制点对应的投影坐标，默认为0;
    # pixel、line是控制点在图像上的列、行位置，默认为0;
    # info、id是用于说明控制点的描述和点号的可选字符串，默认为空.
    """


def geo():
    in_path = r'C:\Users\Administrator\Desktop\hdf\TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf'
    hdfDs = gdal.Open(in_path)
    hdfSubDsList = hdfDs.GetSubDatasets()
    target_ds = list(filter(lambda x: 'Longitude' in str(x), hdfSubDsList))
    target_list = []
    target_index = hdfSubDsList.index(target_ds[0])
    target_list.append(hdfSubDsList[target_index][0])
    refDs = gdal.Open(target_list[0])

    bandArray1 = refDs.GetRasterBand(1).ReadAsArray()
    bandArray1 = bandArray1[0:2480, :]
    outBand1 = r'C:\Users\Administrator\Desktop\hdf\Longitude.tif'
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outBand1, bandArray1.shape[1], bandArray1.shape[0], 1, gdal.GDT_Float32)
    ds.GetRasterBand(1).WriteArray(bandArray1)
    ds = None

    print('a')


def vrt():
    pass

    """
    gdalwarp -geoloc C:/Users/Administrator/Desktop/hdf/vrtTest.vrt C:/Users/Administrator/Desktop/hdf/vrtTest.tif
    
    
    HDF4_EOS:EOS_SWATH:"C:/Users/Administrator/Desktop/hdf/TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf":MODIS_SWATH_Type_L1B:EV_250_RefSB
    
    C:/hegWINv2.15.Build9.8/HEG_Win/bin/swtif -P HegSwath.prm > heg.log
    
    """


if __name__ == '__main__':

    hdf_name = r'C:\Users\Administrator\Desktop\hdf\TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf'
    hdf_obj = SD(hdf_name, SDC.READ)
    hdf_obj_attributes = hdf_obj.attributes()
    with open(r'C:\Users\Administrator\Desktop\temp\hdfpy_metadata.txt', 'w') as f:
        for key in hdf_obj_attributes.keys():
            f.write('%s : %s' % (key, hdf_obj_attributes[key]))
            f.write('\n')

    in_path = r'C:\Users\Administrator\Desktop\hdf\TERRA_X_2020_10_12_11_21_D_G.MOD02QKM.hdf'
    hdfDs = gdal.Open(in_path)
    with open(r'C:\Users\Administrator\Desktop\temp\gdal_metadata.txt', 'w') as f:
        for key in hdfDs.GetMetadata().keys():
            f.write('%s : %s' % (key, hdfDs.GetMetadata()[key]))
            f.write('\n')
            if key not in hdf_obj_attributes.keys():
                print(key)
    print('Finish')


