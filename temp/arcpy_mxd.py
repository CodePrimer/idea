# -*- coding: utf-8 -*-
import arcpy
import os


if __name__ == '__main__':

    mxd_path = r'C:\Users\Administrator\Desktop\taihumxd\1_10.2.mxd'
    # mxd_path = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\mxd\1.mxd'
    mxd = arcpy.mapping.MapDocument(mxd_path)

    for df in arcpy.mapping.ListDataFrames(mxd):
        if df.name == 'Layers':
            print(df.extent)
            layers = arcpy.mapping.ListLayers(mxd, '数据框中指定图层_name', df)
        # for layer in layers:
        #     df.extent = layer.getExtent()

    print('a')