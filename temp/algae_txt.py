# -*- coding: utf-8 -*-

import os
from temp.MySqlCustom import SQLStringInterface
from temp.MySqlCustom import executeSql


if __name__ == '__main__':
    rootDir = r'C:\Users\Administrator\Desktop\2020年蓝藻日报'
    txtFileList = os.listdir(rootDir)

    sqlLoginInfo = {'host': "127.0.0.1",
                    'dbname': "jiangsu_water",
                    'user': "root",
                    'pwd': "123456",
                    'port': 3306}

    for txtName in txtFileList:
        txtPath = os.path.join(rootDir, txtName)

        # 01 全云
        sample01 = '太湖全部被云层覆盖，无法判断蓝藻聚集情况'
        # 02 有云无藻
        sample02 = '太湖部分湖区被云层覆盖，无云区域内未发现蓝藻聚集现象'
        # 03 有云有藻
        sample03 = '太湖部分湖区被云层覆盖，无云区域内发现蓝藻聚集面积约'
        # 04 无云无藻
        sample04 = '太湖未发现蓝藻聚集现象'
        # 05 无云有藻
        sample05 = '太湖发现蓝藻聚集面积约'

        with open(txtPath, 'r') as f:
            txtContext = f.readline()
            txtContext = txtContext.replace('平方千米', '平方公里')
            # print(txtContext)
            splitResult = txtContext.split('EOS/MODIS')
            timeStr = splitResult[0]
            monthStr = timeStr.split('月')[0]
            dayStr = timeStr.split('月')[1].split('日')[0]
            hourStr = timeStr.split('月')[1].split('日')[1].split('时')[0]
            minuteStr = timeStr.split('月')[1].split('日')[1].split('时')[1].split('分')[0]
            month = '%02d' % int(monthStr)
            day = '%02d' % int(dayStr)
            hour = '%02d' % int(hourStr)
            minute = '%02d' % int(minuteStr)
            # 时间
            datetimeStr = '2020-%s-%s %s:%s:00' % (month, day, hour, minute)

            if sample01 in txtContext:
                cloud = '100'
                area = '0'
            elif sample02 in txtContext:
                cloud = '50'
                area = '0'
            elif sample03 in txtContext:
                cloud = '50'
                tempStr1 = txtContext.split('平方公里')[0]
                area = tempStr1.split(sample03)[1]
            elif sample04 in txtContext:
                cloud = '0'
                area = '0'
            elif sample05 in txtContext:
                cloud = '0'
                tempStr1 = txtContext.split('平方公里')[0]
                area = tempStr1.split(sample05)[1]
            else:
                print('ERROR:%s' % datetimeStr)
                continue

            if cloud == '100':
                cloudType = 1
            elif cloud == '50':
                cloudType = 2
            elif cloud == '0':
                cloudType = 3
            else:
                cloudType = ''

            SQL_QUERY = 'SELECT area,cloud FROM t_water_taihu_modis WHERE date={datetimeStr};'
            SQL_INSERT = 'INSERT INTO t_water_taihu_modis (date,area,cloud) VALUES {values};'

            sqlData = {'datetimeStr': datetimeStr}
            sqlStr = SQLStringInterface(SQL_QUERY, sqlData)
            sqlRes = executeSql(sqlLoginInfo, sqlStr)
            if len(sqlRes) != 0:
                sql_area = str(sqlRes[0][0])
                sql_cloud = sqlRes[0][1]
                if sql_cloud >= 95:
                    sqlCloudType = 1
                elif sql_cloud <= 5:
                    sqlCloudType = 3
                else:
                    sqlCloudType = 2

                # if sql_area != area:
                #     print('Area ERROR:%s' % datetimeStr)
                #     print(txtContext)
                #     print('\n')
                # if sqlCloudType != cloudType:
                #     print('Cloud ERROR:%s' % datetimeStr)
                #     print(txtContext)
                #     print('\n')

            else:
                # 数据库添加记录
                sqlData = {'values': (datetimeStr, area, cloud)}
                sqlStr = SQLStringInterface(SQL_INSERT, sqlData)
                executeSql(sqlLoginInfo, sqlStr)
    print('Finish')