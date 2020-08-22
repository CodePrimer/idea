# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/19 9:02

"""江苏水环境平台批量添加数据 -- 饮用水源地"""

import os
import arcpy
from arcpy.sa import *

# from ShapeUtil import ShapeUtil


# def copyFile():
#     sourceDir = r'F:\zktq\江苏省水源地矢量\ok'
#     copyDir = r'F:\zktq\shuiyuandi'
#     for d in os.listdir(sourceDir):
#         # 数据库查询
#         conn = pymysql.connect(
#             db='jiangsu_water',
#             user='root',
#             password='jsem_water_mysql_2020',
#             host='192.168.50.8',
#             port=3306)
#         cursor = conn.cursor()
#         tableName = 't_water_yinyongshui'  # 查询表名
#         sqlStr = "SELECT uuid FROM %s WHERE fullname='%s';" % (tableName, d)
#         cursor.execute(sqlStr)
#         sqlResult = cursor.fetchall()[0][0]
#         shpDir = os.path.join(sourceDir, d, 'A')
#         for f in os.listdir(shpDir):
#             if f.endswith('.shp'):
#                 shpFilePath = os.path.join(shpDir, f)
#                 # print(shpFilePath)
#                 copySubDir = os.path.join(copyDir, sqlResult)
#                 os.makedirs(copySubDir)
#                 ShapeUtil.copyFile_os(shpFilePath, copySubDir, targetName=sqlResult)
#     print('Finish')

#
# conn = pymysql.connect(
#     db='jiangsu_water',
#     user='root',
#     password='jsem_water_mysql_2020',
#     host='192.168.50.8',
#     port=3306)
# cursor = conn.cursor()
# tableName = 't_water_yinyongshui'  # 查询表名
# sqlStr = "SELECT uuid,city FROM %s;" % tableName
# cursor.execute(sqlStr)
# sqlResult = cursor.fetchall()
# searchDict = {'南京市': 'nanjingshi', '无锡市': 'wuxishi', '徐州市': 'xuzhoushi', '常州市': 'changzhoushi',
#               '苏州市': 'suzhoushi', '南通市': 'nantongshi', '连云港市': 'lianyungang', '淮安市': 'huaianshi',
#               '盐城市': 'yanchengshi', '扬州市': 'yangzhoushi', '镇江市': 'zhenjiangshi', '泰州市': 'taizhoushi',
#               '宿迁市': 'suqianshi'}
# resultDict = {}
# for each in sqlResult:
#     uuid = each[0]
#     city = searchDict[each[1]]
#     resultDict[uuid] = city
# print('Finish')

if __name__ == '__main__':

    # copyFile()

    inputDir = r'F:\zktq\shuiyuandi'

    classList = [u'\u5de5\u4e1a\u7528\u5730', u'\u5c45\u6c11\u70b9_\u519c\u6751', u'\u4eba\u5de5\u5f00\u53d1',
                 u'\u519c\u4e1a\u7528\u5730_\u81ea\u7136\u79cd\u690d', u'\u6c34\u4ea7\u517b\u6b96',
                 u'\u9646\u5730\u8fd0\u8f93_\u516c\u8def', u'\u6c34\u4f53',
                 u'\u519c\u4e1a\u7528\u5730_\u519c\u4e1a\u8bbe\u65bd\u7528\u5730',
                 u'\u519c\u4e1a\u7528\u5730_\u5927\u68da\u79cd\u690d', u'\u6797\u5730_\u81ea\u7136\u6797',
                 u'\u8349\u5730_\u57ce\u5e02\u7eff\u5730', u'\u8349\u5730_\u81ea\u7136\u8349\u5730',
                 u'\u755c\u79bd\u517b\u6b96', u'\u5c45\u6c11\u70b9_\u57ce\u9547',
                 u'\u5f00\u91c7\u7528\u5730_\u53d6\u571f', u'\u6797\u5730_\u4eba\u5de5\u6797',
                 u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u6cb3\u6ee9\u5730',
                 u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u88f8\u5730',
                 u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u6ee9\u6d82', u'\u6c34\u4f53_\u5927\u575d',
                 u'\u6c34\u4e0a\u8fd0\u8f93_\u6c34\u4e0a\u8239\u53ea', u'\u6c34\u4f53_\u5e72\u67af\u6cb3\u9053',
                 u'\u529e\u516c\u7528\u5730_\u5546\u4e1a', u'\u529e\u516c\u7528\u5730_\u5b66\u6821',
                 u'\u5f00\u91c7\u7528\u5730', u'\u65c5\u6e38\u7528\u5730_\u516c\u56ed',
                 u'\u6c34\u4e0a\u8fd0\u8f93_\u7801\u5934', u'\u6c34\u4e0a\u8fd0\u8f93_\u6e2f\u53e3',
                 u'\u65c5\u6e38\u7528\u5730_\u5ea6\u5047\u6751', u'\u529e\u516c\u7528\u5730_\u673a\u5173',
                 u'\u9646\u5730\u8fd0\u8f93_\u670d\u52a1\u533a', u'\u5176\u5b83\u81ea\u7136\u7528\u5730',
                 u'\u5de5\u4e1a\u7528\u5730_\u5176\u4ed6\u5de5\u4e1a\u7528\u5730',
                 u'\u519c\u4e1a\u7528\u5730_\u519c\u4e1a\u8bbe\u65bd\u7528?', u'\u9646\u5730\u8fd0\u8f93_\u94c1\u8def',
                 u'\u519c\u4e1a\u7528\u5730_\u519c\u4e1a\u8bbe\u65bd\u7528',
                 u'\u65c5\u6e38\u7528\u5730_\u9ad8\u5c14\u592b\u7403\u573a',
                 u'\u9646\u5730\u8fd0\u8f93_\u6536\u8d39\u7ad9', u'\u9646\u5730\u8fd0\u8f93_\u673a\u573a',
                 u'\u529e\u516c\u7528\u5730', u'\u9646\u5730\u8fd0\u8f93_ \u670d\u52a1\u533a',
                 u'\u5de5\u4e1a\u7528\u5730_\u5176\u5b83\u5de5\u4e1a\u7528\u5730',
                 u'\u5f00\u91c7\u7528\u5730_\u91c7\u77ff', u'\u65c5\u6e38\u7528\u5730',
                 u'\u519c\u4e1a\u7528\u5730_\u81ea\u7136\u79cd\u503c', u'\u8349\u5730_\u81ea\u7136\u7eff\u5730',
                 u'\u5de5\u4e1a\u7528\u5730_\u4f01\u4e1a']
    # classList = sorted(classList)
    # for each in classList:
    #     print(each)
    replaceDict = {u'农业用地_农业设施用?': u'农业用地_农业设施用地',
                   u'农业用地_农业设施用': u'农业用地_农业设施用地',
                   u'农业用地_自然种值': u'农业用地_自然种植',
                   u'工业用地_其他工业用地': u'工业用地_其它工业用地',
                   u'草地_自然草地': u'草地_自然绿地',
                   u'陆地运输_ 服务区': u'陆地运输_服务区'}
    # # 1.清洗数据
    # for d in os.listdir(inputDir):
    #     shpPath = os.path.join(inputDir, d, d + '.shp')
    #     print(shpPath)
    #
    #     cursor = arcpy.UpdateCursor(shpPath)
    #     for row in cursor:
    #         className = row.getValue('NAME')
    #         if className in replaceDict.keys():
    #             print(className)
    #             print(replaceDict[className])
    #             row.setValue('NAME', replaceDict[className])
    #         cursor.updateRow(row)

    # 2.添加整型字段
    classDict = {u'\u5f00\u91c7\u7528\u5730_\u53d6\u571f': 19, u'\u6c34\u4e0a\u8fd0\u8f93_\u7801\u5934': 29, u'\u6c34\u4e0a\u8fd0\u8f93_\u6c34\u4e0a\u8239\u53ea': 27, u'\u5f00\u91c7\u7528\u5730': 18, u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u6ee9\u6d82': 4, u'\u5c45\u6c11\u70b9_\u57ce\u9547': 14, u'\u519c\u4e1a\u7528\u5730_\u519c\u4e1a\u8bbe\u65bd\u7528\u5730': 6, u'\u9646\u5730\u8fd0\u8f93_\u94c1\u8def': 41, u'\u6797\u5730_\u81ea\u7136\u6797': 26, u'\u5de5\u4e1a\u7528\u5730_\u5176\u5b83\u5de5\u4e1a\u7528\u5730': 17, u'\u6c34\u4ea7\u517b\u6b96': 30, u'\u6c34\u4f53': 31, u'\u519c\u4e1a\u7528\u5730_\u81ea\u7136\u79cd\u690d': 8, u'\u529e\u516c\u7528\u5730_\u5b66\u6821': 11, u'\u8349\u5730_\u81ea\u7136\u7eff\u5730': 36, u'\u5de5\u4e1a\u7528\u5730': 15, u'\u755c\u79bd\u517b\u6b96': 34, u'\u65c5\u6e38\u7528\u5730': 21, u'\u65c5\u6e38\u7528\u5730_\u9ad8\u5c14\u592b\u7403\u573a': 24, u'\u6c34\u4e0a\u8fd0\u8f93_\u6e2f\u53e3': 28, u'\u9646\u5730\u8fd0\u8f93_\u670d\u52a1\u533a': 39, u'\u519c\u4e1a\u7528\u5730_\u5927\u68da\u79cd\u690d': 7, u'\u6797\u5730_\u4eba\u5de5\u6797': 25, u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u6cb3\u6ee9\u5730': 3, u'\u529e\u516c\u7528\u5730_\u673a\u5173': 12, u'\u65c5\u6e38\u7528\u5730_\u5ea6\u5047\u6751': 23, u'\u9646\u5730\u8fd0\u8f93_\u673a\u573a': 40, u'\u9646\u5730\u8fd0\u8f93_\u6536\u8d39\u7ad9': 38, u'\u529e\u516c\u7528\u5730': 9, u'\u5c45\u6c11\u70b9_\u519c\u6751': 13, u'\u6c34\u4f53_\u5927\u575d': 32, u'\u9646\u5730\u8fd0\u8f93_\u516c\u8def': 37, u'\u5f00\u91c7\u7528\u5730_\u91c7\u77ff': 20, u'\u5de5\u4e1a\u7528\u5730_\u4f01\u4e1a': 16, u'\u4eba\u5de5\u5f00\u53d1': 1, u'\u8349\u5730_\u57ce\u5e02\u7eff\u5730': 35, u'\u5176\u5b83\u81ea\u7136\u7528\u5730_\u88f8\u5730': 5, u'\u6c34\u4f53_\u5e72\u67af\u6cb3\u9053': 33, u'\u5176\u5b83\u81ea\u7136\u7528\u5730': 2, u'\u65c5\u6e38\u7528\u5730_\u516c\u56ed': 22, u'\u529e\u516c\u7528\u5730_\u5546\u4e1a': 10}
    # for d in os.listdir(inputDir):
    #     shpPath = os.path.join(inputDir, d, d + '.shp')
    #     print(shpPath)
    #     arcpy.AddField_management(shpPath, "value", "SHORT")
    #     cursor = arcpy.UpdateCursor(shpPath)
    #     for row in cursor:
    #         className = row.getValue('NAME')
    #         print(classDict[className])
    #         row.setValue('value', classDict[className])
    #         cursor.updateRow(row)

    # 3.矢量转栅格 外加裁切
    sumCount = len(os.listdir(inputDir))
    count = 0
    for d in os.listdir(inputDir):
        print(str(count) + '//' + str(sumCount))
        count += 1
        shpPath = os.path.join(inputDir, d, d + '.shp')
        # 转栅格结果
        outRasterDir = os.path.join(r'F:\zktq\shuiyuandi_result', d, 'raster')
        if not os.path.exists(outRasterDir):
            os.makedirs(outRasterDir)
        outRaster = os.path.join(outRasterDir, d + '.tif')
        arcpy.PolygonToRaster_conversion(shpPath, 'value', outRaster, 'CELL_CENTER', 'NONE', 0.00002)

        # 裁切结果
        outRGBDir = os.path.join(r'F:\zktq\shuiyuandi_result', d, 'rgb')
        if not os.path.exists(outRGBDir):
            os.makedirs(outRGBDir)
        cityDict = {'d988ad62-ddce-11ea-866a-701ce7f77dbb': 'changzhoushi',
                    'd98a80ec-ddce-11ea-b86f-701ce7f77dbb': 'changzhoushi',
                    'd98c7b50-ddce-11ea-8a18-701ce7f77dbb': 'changzhoushi',
                    'd98e2830-ddce-11ea-8107-701ce7f77dbb': 'changzhoushi',
                    'd9902254-ddce-11ea-a339-701ce7f77dbb': 'changzhoushi',
                    'd992df8c-ddce-11ea-87a4-701ce7f77dbb': 'huaianshi',
                    'd99611b0-ddce-11ea-ace2-701ce7f77dbb': 'huaianshi',
                    'd9972262-ddce-11ea-9788-701ce7f77dbb': 'huaianshi',
                    'd998816e-ddce-11ea-b81b-701ce7f77dbb': 'huaianshi',
                    'd99a2d9e-ddce-11ea-8f31-701ce7f77dbb': 'huaianshi',
                    'd99b3e42-ddce-11ea-8a6d-701ce7f77dbb': 'huaianshi',
                    'd99d38e2-ddce-11ea-a8ac-701ce7f77dbb': 'huaianshi',
                    'd99e976c-ddce-11ea-9f66-701ce7f77dbb': 'huaianshi',
                    'd9a091cc-ddce-11ea-9caf-701ce7f77dbb': 'huaianshi',
                    'd9a1c986-ddce-11ea-8d8d-701ce7f77dbb': 'huaianshi',
                    'd9a3282e-ddce-11ea-8e64-701ce7f77dbb': 'huaianshi',
                    'd9a4fba6-ddce-11ea-b6ea-701ce7f77dbb': 'huaianshi',
                    'd9a6334c-ddce-11ea-85bd-701ce7f77dbb': 'lianyungang',
                    'd9a791ee-ddce-11ea-82cb-701ce7f77dbb': 'lianyungang',
                    'd9a8f0ac-ddce-11ea-b0bd-701ce7f77dbb': 'lianyungang',
                    'd9aa7638-ddce-11ea-8c54-701ce7f77dbb': 'lianyungang',
                    'd9af7bb6-ddce-11ea-819e-701ce7f77dbb': 'lianyungang',
                    'd9b1285c-ddce-11ea-b4e3-701ce7f77dbb': 'lianyungang',
                    'd9b25ff4-ddce-11ea-ab20-701ce7f77dbb': 'lianyungang',
                    'd9b3e58c-ddce-11ea-bf70-701ce7f77dbb': 'lianyungang',
                    'd9b51d3a-ddce-11ea-82ff-701ce7f77dbb': 'lianyungang',
                    'd9b654dc-ddce-11ea-a805-701ce7f77dbb': 'lianyungang',
                    'd9b7da70-ddce-11ea-ad2c-701ce7f77dbb': 'lianyungang',
                    'd9b9adf4-ddce-11ea-a71a-701ce7f77dbb': 'nanjingshi',
                    'd9bb5a88-ddce-11ea-88d5-701ce7f77dbb': 'nanjingshi',
                    'd9bcb918-ddce-11ea-95a0-701ce7f77dbb': 'nanjingshi',
                    'd9bdf0ca-ddce-11ea-b954-701ce7f77dbb': 'nanjingshi',
                    'd9bfc43a-ddce-11ea-973b-701ce7f77dbb': 'nanjingshi',
                    'd9c0fbf4-ddce-11ea-a46e-701ce7f77dbb': 'nanjingshi',
                    'd9c25a8c-ddce-11ea-84fb-701ce7f77dbb': 'nanjingshi',
                    'd9c39258-ddce-11ea-a1c5-701ce7f77dbb': 'nanjingshi',
                    'd9c565e4-ddce-11ea-8579-701ce7f77dbb': 'nanjingshi',
                    'd9c6c45c-ddce-11ea-a127-701ce7f77dbb': 'nanjingshi',
                    'd9c82300-ddce-11ea-a840-701ce7f77dbb': 'nanjingshi',
                    'd9c98190-ddce-11ea-bd28-701ce7f77dbb': 'nantongshi',
                    'd9cab952-ddce-11ea-b9c9-701ce7f77dbb': 'nantongshi',
                    'd9cbf0ee-ddce-11ea-9038-701ce7f77dbb': 'nantongshi',
                    'd9cd4f98-ddce-11ea-913d-701ce7f77dbb': 'nantongshi',
                    'd9ced526-ddce-11ea-8cb2-701ce7f77dbb': 'nantongshi',
                    'd9d00cd0-ddce-11ea-a0af-701ce7f77dbb': 'nantongshi',
                    'd9d365dc-ddce-11ea-a600-701ce7f77dbb': 'nantongshi',
                    'd9d4c482-ddce-11ea-a7e8-701ce7f77dbb': 'nantongshi',
                    'd9d64a24-ddce-11ea-b9bb-701ce7f77dbb': 'nantongshi',
                    'd9d781ca-ddce-11ea-a9cf-701ce7f77dbb': 'nantongshi',
                    'd9db28c6-ddce-11ea-9274-701ce7f77dbb': 'suzhoushi',
                    'd9dc8766-ddce-11ea-b9a8-701ce7f77dbb': 'suzhoushi',
                    'd9de33e4-ddce-11ea-8358-701ce7f77dbb': 'suzhoushi',
                    'd9df6ba2-ddce-11ea-b67f-701ce7f77dbb': 'suzhoushi',
                    'd9e0a340-ddce-11ea-a04a-701ce7f77dbb': 'suzhoushi',
                    'd9e312a4-ddce-11ea-b6d1-701ce7f77dbb': 'suzhoushi',
                    'd9e44a42-ddce-11ea-b858-701ce7f77dbb': 'suzhoushi',
                    'd9e5f6d0-ddce-11ea-9905-701ce7f77dbb': 'suzhoushi',
                    'd9e7a354-ddce-11ea-9b40-701ce7f77dbb': 'suzhoushi',
                    'd9e901f4-ddce-11ea-88aa-701ce7f77dbb': 'suzhoushi',
                    'd9eaae82-ddce-11ea-a1bb-701ce7f77dbb': 'suzhoushi',
                    'd9ec341e-ddce-11ea-8ddc-701ce7f77dbb': 'suzhoushi',
                    'd9ede0a2-ddce-11ea-847c-701ce7f77dbb': 'suzhoushi',
                    'd9eef15e-ddce-11ea-a91d-701ce7f77dbb': 'suzhoushi',
                    'd9f028fe-ddce-11ea-aae1-701ce7f77dbb': 'suzhoushi',
                    'd9f1879e-ddce-11ea-8d2d-701ce7f77dbb': 'taizhoushi',
                    'd9f4b9c0-ddce-11ea-9ada-701ce7f77dbb': 'taizhoushi',
                    'd9f61864-ddce-11ea-a4aa-701ce7f77dbb': 'taizhoushi',
                    'd9f75008-ddce-11ea-b33d-701ce7f77dbb': 'taizhoushi',
                    'd9f887d2-ddce-11ea-8598-701ce7f77dbb': 'taizhoushi',
                    'd9f9bf58-ddce-11ea-9a6a-701ce7f77dbb': 'taizhoushi',
                    'd9fb6be4-ddce-11ea-8874-701ce7f77dbb': 'wuxishi',
                    'd9fd1880-ddce-11ea-a44a-701ce7f77dbb': 'wuxishi',
                    'da00718a-ddce-11ea-a48c-701ce7f77dbb': 'wuxishi',
                    'da01f71e-ddce-11ea-a70c-701ce7f77dbb': 'wuxishi',
                    'da02e0e8-ddce-11ea-b154-701ce7f77dbb': 'wuxishi',
                    'da043f9e-ddce-11ea-8b95-701ce7f77dbb': 'wuxishi',
                    'da05c546-ddce-11ea-83b0-701ce7f77dbb': 'wuxishi',
                    'da0a2ee4-ddce-11ea-b969-701ce7f77dbb': 'wuxishi',
                    'da0b189a-ddce-11ea-a056-701ce7f77dbb': 'suqianshi',
                    'da0c773a-ddce-11ea-918b-701ce7f77dbb': 'suqianshi',
                    'da123fae-ddce-11ea-bbb6-701ce7f77dbb': 'suqianshi',
                    'da15e6a2-ddce-11ea-a378-701ce7f77dbb': 'suqianshi',
                    'da174546-ddce-11ea-8961-701ce7f77dbb': 'suqianshi',
                    'da18f1da-ddce-11ea-82e2-701ce7f77dbb': 'suqianshi',
                    'da1a5068-ddce-11ea-9da2-701ce7f77dbb': 'suqianshi',
                    'da1baf10-ddce-11ea-8f06-701ce7f77dbb': 'suqianshi',
                    'da1d34a4-ddce-11ea-8ccc-701ce7f77dbb': 'suqianshi',
                    'da1e6c62-ddce-11ea-a542-701ce7f77dbb': 'suqianshi',
                    'da1fcaee-ddce-11ea-84de-701ce7f77dbb': 'suqianshi',
                    'da212998-ddce-11ea-ba15-701ce7f77dbb': 'suqianshi',
                    'da22614c-ddce-11ea-857f-701ce7f77dbb': 'suqianshi',
                    'da240dc6-ddce-11ea-bac0-701ce7f77dbb': 'suqianshi',
                    'da254568-ddce-11ea-a6f8-701ce7f77dbb': 'xuzhoushi',
                    'da26a40c-ddce-11ea-8bac-701ce7f77dbb': 'xuzhoushi',
                    'da2802b4-ddce-11ea-a862-701ce7f77dbb': 'xuzhoushi',
                    'da298840-ddce-11ea-86a4-701ce7f77dbb': 'xuzhoushi',
                    'da2a9908-ddce-11ea-89ad-701ce7f77dbb': 'xuzhoushi',
                    'da2c1e86-ddce-11ea-84c0-701ce7f77dbb': 'xuzhoushi',
                    'da2d5646-ddce-11ea-8dd5-701ce7f77dbb': 'yanchengshi',
                    'da2e8dde-ddce-11ea-8444-701ce7f77dbb': 'yanchengshi',
                    'da2fec8a-ddce-11ea-8c40-701ce7f77dbb': 'yanchengshi',
                    'da31245c-ddce-11ea-a23e-701ce7f77dbb': 'yanchengshi',
                    'da32a9dc-ddce-11ea-adc8-701ce7f77dbb': 'yanchengshi',
                    'da3602dc-ddce-11ea-be68-701ce7f77dbb': 'yanchengshi',
                    'da371392-ddce-11ea-b2dc-701ce7f77dbb': 'yanchengshi',
                    'da384b34-ddce-11ea-aa72-701ce7f77dbb': 'yanchengshi',
                    'da39d0e2-ddce-11ea-9c6e-701ce7f77dbb': 'yanchengshi',
                    'da3b5664-ddce-11ea-aad8-701ce7f77dbb': 'yanchengshi',
                    'da3d9ecc-ddce-11ea-8258-701ce7f77dbb': 'yanchengshi',
                    'da3fe72c-ddce-11ea-803c-701ce7f77dbb': 'yanchengshi',
                    'da427e06-ddce-11ea-991b-701ce7f77dbb': 'yanchengshi',
                    'da43dc10-ddce-11ea-8dc6-701ce7f77dbb': 'yanchengshi',
                    'da44c5da-ddce-11ea-b08d-701ce7f77dbb': 'yangzhoushi',
                    'da46246c-ddce-11ea-aca0-701ce7f77dbb': 'yangzhoushi',
                    'da47a9fa-ddce-11ea-82ff-701ce7f77dbb': 'yangzhoushi',
                    'da49a486-ddce-11ea-8928-701ce7f77dbb': 'yangzhoushi',
                    'da4b9eee-ddce-11ea-ac67-701ce7f77dbb': 'yangzhoushi',
                    'da4caf9c-ddce-11ea-b946-701ce7f77dbb': 'yangzhoushi',
                    'da4e0e42-ddce-11ea-9bac-701ce7f77dbb': 'yangzhoushi',
                    'da4f45ee-ddce-11ea-a774-701ce7f77dbb': 'yangzhoushi',
                    'da50cb8a-ddce-11ea-9d87-701ce7f77dbb': 'yangzhoushi',
                    'da52032e-ddce-11ea-99f1-701ce7f77dbb': 'yangzhoushi',
                    'da53afb4-ddce-11ea-af55-701ce7f77dbb': 'yangzhoushi',
                    'da550e64-ddce-11ea-8d5f-701ce7f77dbb': 'yangzhoushi',
                    'da566d0a-ddce-11ea-9330-701ce7f77dbb': 'zhenjiangshi',
                    'da57a49c-ddce-11ea-8a7b-701ce7f77dbb': 'zhenjiangshi',
                    'da59035e-ddce-11ea-8386-701ce7f77dbb': 'zhenjiangshi',
                    'da5a3ae2-ddce-11ea-a448-701ce7f77dbb': 'zhenjiangshi',
                    'da5b9992-ddce-11ea-bf61-701ce7f77dbb': 'zhenjiangshi'}
        inRaster = os.path.join(r'F:\zktq\jiangsu', cityDict[d], cityDict[d] + '.tif')
        arcpy.CheckOutExtension("Spatial")
        outExtractByMask = ExtractByMask(inRaster, shpPath)
        outExtractTif = os.path.join(outRGBDir, d+'.tif')
        outExtractByMask.save(outExtractTif)

    print('Finish')

