# -*- coding: utf-8  -*-

import os
import re
import sys
import time
import zipfile
import logging
import shutil
import subprocess
import platform
from xml.dom import minidom

import gdal
import numpy as np
import osr

"""哨兵2A数据辐射定标、大气校正、几何校正函数"""

# 哨兵2光学波段中心波长
SENTINEL2_BAND_INFO = {'B01': '443nm', 'B02': '490nm', 'B03': '560nm', 'B04': '665nm', 'B05': '705nm', 'B06': '740nm',
                       'B07': '783nm', 'B08': '842nm', 'B8A': '865nm', 'B09': '945nm', 'B10': '1375nm', 'B11': '1610nm',
                       'B12': '2190nm'}

# 本程序支持处理的哨兵2的波段索引
PROCESS_BAND_INDEX = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B10', 'B11', 'B12']

# 官方大气校正模块Sen2Cor路径
SEN_2_COR_PATH_WINDOWS = 'C:/Users/Administrator/Downloads/Sen2Cor-02.08.00-win64/L2A_Process.bat'
SEN_2_COR_PATH_LINUX = "/home/yunnan/wangbin/Sen2Cor-02.08.00-Linux64/bin/L2A_Process"


class Sentinel2(object):

    @staticmethod
    def unzip(src_file, dest_dir):
        zf = zipfile.ZipFile(src_file)
        try:
            zf.extractall(path=dest_dir)
        except RuntimeError as e:
            print(e)
        zf.close()

    @staticmethod
    def doCmd(cmdStr, timeOutSeconds=60 * 60):
        """启动应用程序进程 默认超时时间10分钟"""
        p = subprocess.Popen(cmdStr, close_fds=True)
        tBegin = time.time()
        while True:
            if p.poll() is not None:
                break
            secondsDelay = time.time() - tBegin
            if secondsDelay > timeOutSeconds:
                p.kill()
                raise TimeoutError("cmd Time out" + str(timeOutSeconds) + "s " + cmdStr)
            time.sleep(5)

    @staticmethod
    def doShell(shellStr, timeOutSeconds=60 * 60):
        """启动应用程序进程 默认超时时间10分钟"""
        p = subprocess.Popen(shellStr, close_fds=True, shell=True)
        tBegin = time.time()
        while True:
            if p.poll() is not None:
                break
            secondsDelay = time.time() - tBegin
            if secondsDelay > timeOutSeconds:
                p.kill()
                raise TimeoutError("cmd Time out" + str(timeOutSeconds) + "s " + shellStr)
            time.sleep(5)

    @staticmethod
    def remove_dir(dir_path):
        """
        删除文件夹
        :param dir_path: 删除文件夹路径
        :return: True - 删除成功 False - 删除失败
        """
        try:
            if not os.path.isdir(dir_path):
                return False
            else:
                shutil.rmtree(dir_path)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def main(zip_file, out_dir, temp_dir):
        # 0.创建log日志，日志文件放在运行py同级的log文件夹下
        log_dir = os.path.join(os.path.dirname(__file__), 'log')
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        log_file_name = os.path.basename(zip_file).split('.')[0] + '.log'
        log_file_path = os.path.join(log_dir, log_file_name)
        log = Logger(log_file_path).get_log
        log.info('Start Sentinel2 process.')

        # 1.解压缩文件
        cur_temp_dir = os.path.join(temp_dir, str(int(time.time() * 100)))
        if not os.path.isdir(cur_temp_dir):
            os.makedirs(cur_temp_dir)
        Sentinel2.unzip(zip_file, cur_temp_dir)
        log.info('Finish unzip file.')

        # 2.调用Sen2Cor
        # bat路径 + 解压后文件路径 + 分辨率参数 + 输出文件夹参数
        unzip_file_name = os.path.basename(zip_file).split('.')[0] + '.SAFE'
        unzip_file_dir = os.path.join(cur_temp_dir, unzip_file_name)
        cor_temp_dir = os.path.join(cur_temp_dir, "Sen2CorResult")
        if not os.path.isdir(cor_temp_dir):
            os.makedirs(cor_temp_dir)
        resolution_param = '--resolution 10'
        cor_out_dir = '--output_dir ' + cor_temp_dir

        if platform.system().lower() == 'windows':
            cmd_str = ' '.join([SEN_2_COR_PATH_WINDOWS, unzip_file_dir, resolution_param, cor_out_dir])
            Sentinel2.doCmd(cmd_str)
        elif platform.system().lower() == 'linux':
            shell_str = ' '.join([SEN_2_COR_PATH_LINUX, unzip_file_dir, resolution_param, cor_out_dir])
            Sentinel2.doShell(shell_str)
        else:
            pass
        log.info('Finish Sen2Cor.')

        # 3.添加投影信息
        # 3.1 解析MTD_MSIL2A.xml获取每个波段文件相对位置
        cor_folder = os.listdir(cor_temp_dir)[0]
        mtd_msi_file_path = os.path.join(cor_temp_dir, cor_folder, "MTD_MSIL2A.xml")  # TODO xml文件名被写死
        if not os.path.isfile(mtd_msi_file_path):
            log.error('cannot found MTD_MSIL2A.xml')
            return
        with open(mtd_msi_file_path, 'r') as f:
            xml_data = f.read()
        xml_data = xml_data.replace('\n', '')
        xml_data = xml_data.replace(' ', '')

        # 匹配各分辨率信息
        re_pattern = '<IMAGE_FILE>[a-zA-Z0-9/_]*</IMAGE_FILE>'  # 正则匹配
        match_result = re.findall(re_pattern, xml_data)
        if len(match_result) == 0:
            log.error('cannot find <IMAGE_FILE> node in xml.')
            return

        # IMG_DATA文件夹相对路径
        img_date_path = os.path.join(cor_temp_dir, cor_folder,
                                     os.path.dirname(os.path.dirname(match_result[0][12:-13])))

        # IMG_DATA文件全路径
        image_file = {'R10m': {}, 'R20m': {}, 'R60m': {}}

        for each in match_result:
            relative_path = each[12:-13]        # 相对路径
            band_index = os.path.basename(relative_path).split('_')[2]  # 波段标识
            if band_index not in PROCESS_BAND_INDEX:
                continue
            res_dir_name = os.path.basename(os.path.dirname(relative_path))  # 分辨率文件夹
            absolute_path = os.path.join(cor_temp_dir, cor_folder, relative_path + '.jp2')  # TODO 文件名后缀被写死
            if res_dir_name == 'R10m':
                image_file['R10m'][band_index] = absolute_path
                log.info(absolute_path)
            if res_dir_name == 'R20m':
                image_file['R20m'][band_index] = absolute_path
                log.info(absolute_path)
            if res_dir_name == 'R60m':
                image_file['R60m'][band_index] = absolute_path
                log.info(absolute_path)

        for key in image_file.keys():
            cur_image_file = image_file[key]

            # 各分辨率分别进行LayerStacking
            srs_arr_list = []
            band_info = []
            for band_name in PROCESS_BAND_INDEX:
                if band_name not in cur_image_file.keys():
                    continue
                srs_ds = gdal.Open(cur_image_file[band_name], gdal.GA_ReadOnly)
                srs_arr = srs_ds.GetRasterBand(1).ReadAsArray()
                srs_arr_list.append(srs_arr)
                temp_str = '%s\t%s' % (band_name, SENTINEL2_BAND_INFO[band_name])
                band_info.append(temp_str)
                del srs_ds
            dst_arr = np.array(srs_arr_list)  # LayerStack结果数组

            # 3.3 获取投影信息
            mtd_tl_file = os.path.join(os.path.dirname(img_date_path), 'MTD_TL.xml')
            if not os.path.isfile(mtd_tl_file):
                logging.error('cannot found MTD_TL.xml')
                return
            root_node = minidom.parse(mtd_tl_file).documentElement
            geometric_node = root_node.getElementsByTagName('n1:Geometric_Info')[0]
            # EPSG代码获取
            epsg_str = str(root_node.getElementsByTagName('HORIZONTAL_CS_CODE')[0].firstChild.data)
            epsg_code = int(epsg_str.replace('EPSG:', ''))

            geoposition_nodes = geometric_node.getElementsByTagName('Geoposition')
            ulx = None      # 左上角点坐标
            uly = None
            xres = None     # 分辨率
            yres = None
            for nd in geoposition_nodes:
                if nd.getAttribute('resolution') != key[1:3]:
                    continue
                ulx = int(nd.getElementsByTagName('ULX')[0].firstChild.data)
                uly = int(nd.getElementsByTagName('ULY')[0].firstChild.data)
                xres = int(nd.getElementsByTagName('XDIM')[0].firstChild.data)
                yres = int(nd.getElementsByTagName('YDIM')[0].firstChild.data)

            # 3.4 输出tif和波段信息
            dst_sr = osr.SpatialReference()
            dst_sr.ImportFromEPSG(epsg_code)
            dst_geo_transform = [ulx, xres, 0, uly, 0, yres]
            dst_width = dst_arr.shape[2]
            dst_height = dst_arr.shape[1]
            dst_bands = dst_arr.shape[0]

            driver = gdal.GetDriverByName("GTiff")

            out_base_name = os.path.basename(zip_file).split('.')[0] + '_COR_' + key
            out_tif_name = out_base_name + '.TIF'
            out_tif_path = os.path.join(out_dir, out_tif_name)
            dst_ds = driver.Create(out_tif_path, dst_width, dst_height, dst_bands, gdal.GDT_UInt16)
            dst_ds.SetGeoTransform(dst_geo_transform)
            dst_ds.SetProjection(dst_sr.ExportToWkt())
            for i in range(dst_bands):
                dst_ds.GetRasterBand(i + 1).WriteArray(dst_arr[i])
            del dst_ds
            log.info('Save Tif File: %s' % out_tif_path)

            # 写出波段信息
            out_band_file_name = out_base_name + '_BANDINFO.txt'
            out_band_file_path = os.path.join(out_dir, out_band_file_name)
            write_index = 0
            with open(out_band_file_path, 'w') as f:
                f.write('Index\tSentinel2Band\tWavelength\n')
                for each_info in band_info:
                    write_index += 1
                    write_str = '%s\t%s' % (str(write_index), each_info)
                    f.write('%s\n' % write_str)
            log.info('Save Band Info: %s' % out_band_file_path)

        Sentinel2.remove_dir(cur_temp_dir)


class Logger(object):
    def __init__(self, logPath):
        # 创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(logPath, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
        fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s %(filename)s[%(funcName)s line:%(lineno)d] %(levelname)s %(message)s",
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @property
    def get_log(self):
        """定义一个函数，回调logger实例"""
        return self.logger


if __name__ == '__main__':
    """
    @:param zip_file: 压缩文件路径
    @:param temp_dir: 临时目录
    @:param out_dir: 输出文件夹
    """
    zip_file = r"D:\share\Sentinel2Process\01data\S2A_MSIL1C_20200413T023551_N0209_R089_T51RTQ_20200413T042607.zip"
    out_dir = r'D:\share\Sentinel2Process\02output'
    temp_dir = r'D:\share\Sentinel2Process\03temp'

    # args = sys.argv
    # zip_file = args[1]
    # out_dir = args[2]
    # temp_dir = args[3]
    startTime = time.time()
    Sentinel2.main(zip_file, out_dir, temp_dir)
    endTime = time.time()
    print((endTime - startTime)/60)