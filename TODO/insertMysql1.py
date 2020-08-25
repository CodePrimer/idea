# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/22 22:14

import os
import uuid
import time
import datetime
import pymysql


def copy_file(source_file, target_dir, target_name=None):
    """
    复制文件
    :param source_file: 被复制文件路径
    :param target_dir: 目标文件夹
    :param target_name: 复制后文件名（默认不变）
    :return: True - 执行成功 False - 执行失败
    """
    if not os.path.isfile(source_file):
        print("被复制文件不存在.")
        return False
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    try:
        if target_name:
            save_name = target_name
        else:
            save_name = os.path.basename(source_file)
        target_file_path = os.path.join(target_dir, save_name)
        if not os.path.exists(target_file_path) or (
                os.path.exists(target_file_path) and (
                os.path.getsize(target_file_path) != os.path.getsize(source_file))):
            with open(target_file_path, "wb") as ft:
                with open(source_file, "rb") as fs:
                    ft.write(fs.read())
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    rootDir = '/mnt/resource/model/input/JSEM2020'
    copyRootDir = '/mnt/resource/model/output/a6ce588b-ee2c-11e9-b63f-0242ac110009'
    # copyRootDir = 'C:/Users/Think/Desktop/copyDir'
    yearMonthDirList = os.listdir(rootDir)

    tableName = 't_export_image_copy'
    conn = pymysql.connect(db='jiangsu_water',
                           user='root',
                           password='jsem_water_mysql_2020',
                           host='192.168.50.8',
                           port=3306)
    cursor = conn.cursor()

    # sql_id = 'SELECT id FROM %s ORDER BY id DESC LIMIT 1' % tableName
    # cursor.execute(sql_id)
    # count = int(cursor.fetchall()[0][0]) + 1

    count = 245

    for ym in os.listdir(rootDir):
        targetDir = os.path.join(rootDir, ym)
        for f in os.listdir(targetDir):
            if not f.startswith('th'):
                continue
            else:
                if f.endswith('_T.tif'):
                    sensor = 'TERRA'
                elif f.endswith('_A.tif'):
                    sensor = 'AQUA'
                else:
                    print('ERROR:' + f)
                    continue
                issue = '2020' + f[4:8] + '000000'
                copyFileDir = os.path.join(copyRootDir, issue)
                targetFile = os.path.join(targetDir, f)
                if not os.path.exists(copyFileDir):
                    os.makedirs(copyFileDir)
                copyFileName = '%s_MODIS_250_L2_%s_061_00_taihu_algae_ndvi.tif' % (sensor, issue)
                copy_file(targetFile, copyFileDir, target_name=copyFileName)

                # 入数据库
                tb_id = str(count)
                tb_uuid = str(uuid.uuid4())
                tb_path = os.path.join(copyFileDir, copyFileName).replace('\\', '/').replace('/mnt/resource/', '')
                dt = datetime.datetime.strptime(issue, '%Y%m%d%H%M%S')
                tb_acquire_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                tb_process_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                tb_model_uuid = 'a6ce588b-ee2c-11e9-b63f-0242ac110009'
                sqlStr = "INSERT INTO `jiangsu_water`.`%s` " \
                         "(`id`, `uuid`, `name`, `path`, `type`, `model_type`, `satellite`, `sensor`, `lat_lr`, " \
                         "`lon_lr`, `lon_ul`, `lat_ul`, `acquire_time`, `cloud`, `area`, `process_time`, " \
                         "`is_deleted`, `model_uuid`, `colorbar_min`, `colorbar_max`, `colorbar_tick`, " \
                         "`colorbar_color`, `unit`, `is_edit`, `is_edited`) VALUES " \
                         "('%s', '%s', '%s', '%s', 'tif', 'algae', 'EOS', 'MODIS', '30.92980', '120.63700', " \
                         "'119.89200', '31.54600', '%s', '0', '0', '%s', '0', '%s', '0', '1', '', '', '', '1', '1');" \
                         % (tableName, tb_id, tb_uuid, copyFileName, tb_path, tb_acquire_time, tb_process_time,
                            tb_model_uuid)
                cursor.execute(sqlStr)
                conn.commit()
                count += 1
    print('Finish.')