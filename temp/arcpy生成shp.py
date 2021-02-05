# -*- coding: utf-8 -*-

import arcpy
from arcpy import env
import os


if __name__ == '__main__':
    rootpath = r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\utm'
    fc = 'newpoly.shp'
    allpathfc = os.path.join(rootpath, fc)

    sr = arcpy.SpatialReference(r'C:\Users\Administrator\Desktop\jiangsu_water2\depend\taihu\utm\taihu.prj')
    # 建立要素类
    arcpy.CreateFeatureclass_management(rootpath, fc, 'Polygon', spatial_reference=sr)
    # 建立游标对象
    cursor = arcpy.da.InsertCursor(allpathfc, ['SHAPE@'])  # allpathfc 需为全路径，否则会报错
    # 建立点对象数列Array()
    array = arcpy.Array()
    point = arcpy.Point()
    pointList = [[1, 195203.762, 3498433.803],
                 [2, 195203.762, 3420416.355],
                 [3, 280082.543, 3420416.355],
                 [4, 280082.543, 3498433.803]]

    for line in pointList:
        point.ID = line[0]
        point.X = line[1]
        point.Y = line[2]
        array.add(point)
    polygon = arcpy.Polygon(array)

    # 插入游标
    cursor.insertRow([polygon])
    del cursor
    print('Finish')