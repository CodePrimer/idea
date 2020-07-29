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
import gdal
import numpy as np
import osr

"""哨兵2A数据辐射定标、大气校正、几何校正函数"""


class Sentinel2(object):

    # 官方大气校正模块bat路径
    SEN_2_COR_PATH_WINDOWS = "D:/SentinelProcess/Sen2Cor-02.08.00-win64/L2A_Process.bat"
    SEN_2_COR_PATH_LINUX = "/home/yunnan/wangbin/Sen2Cor-02.08.00-Linux64/bin/L2A_Process"

    @staticmethod
    def unzip(src_file, dest_dir):
        zf = zipfile.ZipFile(src_file)
        try:
            zf.extractall(path=dest_dir)
        except RuntimeError as e:
            print(e)
        zf.close()

    @staticmethod
    def doCmd(cmdStr, timeOutSeconds=60 * 10):
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
    def doShell(shellStr, timeOutSeconds=60 * 10):
        """启动应用程序进程 默认超时时间10分钟"""
        p = subprocess.Popen(shellStr, close_fds=True, shell=True)
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
    def main(zip_file, out_dir, temp_dir, res):
        # 0.创建log日志，日志文件放在运行py同级的log文件夹下
        log_dir = os.path.join(os.path.dirname(__file__), 'log')
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        log_file_name = os.path.basename(zip_file).split('.')[0] + '.log'
        log_file_path = os.path.join(log_dir, log_file_name)
        log = Logger(log_file_path).get_log
        log.info('Start Sentinel process.')

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
        resolution_param = '--resolution ' + str(int(res))
        cor_out_dir = '--output_dir ' + cor_temp_dir

        if platform.system().lower() == 'windows':
            cmd_str = ' '.join([Sentinel2.SEN_2_COR_PATH_WINDOWS, unzip_file_dir, resolution_param, cor_out_dir])
            Sentinel2.doCmd(cmd_str)
        elif platform.system().lower() == 'linux':
            shell_str = ' '.join([Sentinel2.SEN_2_COR_PATH_LINUX, unzip_file_dir, resolution_param, cor_out_dir])
            Sentinel2.doShell(shell_str)
        else:
            pass
        log.info('Finish Sen2Cor.')

        # 3.添加投影信息
        # 3.1 解析MTD_MSIL2A.xml获取每个波段文件相对位置
        cor_folder = os.listdir(cor_temp_dir)[0]
        mtd_msi_file_path = os.path.join(cor_temp_dir, cor_folder, "MTD_MSIL2A.xml")  # TODO xml文件名被写死
        if not os.path.isfile(mtd_msi_file_path):
            logging.error('cannot found MTD_MSIL2A.xml')
        with open(mtd_msi_file_path, 'r') as f:
            xml_data = f.read()
        xml_data = xml_data.replace('\n', '')
        xml_data = xml_data.replace(' ', '')
        re_pattern = '<IMAGE_FILE>[a-zA-Z0-9/_]*</IMAGE_FILE>'  # 正则匹配
        match_result = re.findall(re_pattern, xml_data)
        image_file_dict = {}  # 存储各光学波段路径
        # 仅对光学波段进行几何校正，不对SCL/AOT/WVP/TCI等波段进行处理
        available_band_list = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B10', 'B11',
                               'B12']
        for each in match_result:
            # 获取波段信息
            relative_path = each[12:-13]
            band_info = os.path.basename(relative_path).split('_')[2]
            absolute_path = os.path.join(cor_temp_dir, cor_folder, relative_path + '.jp2')  # TODO 文件名后缀被写死
            if band_info in available_band_list:
                image_file_dict[band_info] = absolute_path

        # 3.2 光学波段LayerStacking
        srs_arr_list = []
        band_order = []
        for each in available_band_list:
            if each not in image_file_dict.keys():
                continue
            srs_ds = gdal.Open(image_file_dict[each], gdal.GA_ReadOnly)
            srs_arr = srs_ds.GetRasterBand(1).ReadAsArray()
            # print(srs_arr.shape)
            srs_arr_list.append(srs_arr)
            band_order.append(each)
        dst_arr = np.array(srs_arr_list)  # LayerStack结果数组
        del srs_ds

        # 3.3 获取投影信息
        mtd_tl_file = os.path.join(cor_temp_dir, cor_folder, relative_path[0: relative_path.find('IMG_DATA') - 1],
                                   'MTD_TL.xml')
        if not os.path.isfile(mtd_tl_file):
            logging.error('cannot found MTD_TL.xml')
        with open(mtd_tl_file, 'r') as f:
            xml_data = f.read()
        xml_data = xml_data.replace('\n', '')
        epsg_pattern = '<HORIZONTAL_CS_CODE>EPSG:[0-9]*</HORIZONTAL_CS_CODE>'  # 正则匹配
        epsg_result = re.findall(epsg_pattern, xml_data)[0]
        epsg_code = int(epsg_result[25:-21])  # TODO 截取风险
        geo_pattern = '<Geoposition resolution="60">.*</Geoposition>'
        geo_result = re.findall(geo_pattern, xml_data)[0]
        ulx = int(re.findall('<ULX>[0-9]*</ULX>', geo_result)[0][5:-6])
        uly = int(re.findall('<ULY>[0-9]*</ULY>', geo_result)[0][5:-6])
        xres = int(re.findall('<XDIM>[0-9]*</XDIM>', geo_result)[0][6:-7])
        yres = int(re.findall('<YDIM>.*</YDIM>', geo_result)[0][6:-7])

        # 3.4 输出tif和波段信息
        dst_sr = osr.SpatialReference()
        dst_sr.ImportFromEPSG(epsg_code)
        dst_geo_transform = [ulx, xres, 0, uly, 0, yres]

        driver = gdal.GetDriverByName("GTiff")
        # numpy和gdal数据类型对应表
        dtype_dict = {"uint8": gdal.GDT_Byte, "int16": gdal.GDT_Int16, "int32": gdal.GDT_Int32,
                      "uint16": gdal.GDT_UInt16,
                      "uint32": gdal.GDT_UInt32, "float32": gdal.GDT_Float32, "float64": gdal.GDT_Float64}

        dst_width = dst_arr.shape[2]
        dst_height = dst_arr.shape[1]
        dst_bands = dst_arr.shape[0]

        out_tif_name = os.path.basename(zip_file).split('.')[0] + '_COR.TIF'
        out_tif_path = os.path.join(out_dir, out_tif_name)
        dst_ds = driver.Create(out_tif_path, dst_width, dst_height, dst_bands, dtype_dict[dst_arr.dtype.name])
        dst_ds.SetGeoTransform(dst_geo_transform)
        dst_ds.SetProjection(dst_sr.ExportToWkt())
        for i in range(dst_bands):
            dst_ds.GetRasterBand(i + 1).WriteArray(dst_arr[i])
        del dst_ds

        out_band_file_name = os.path.basename(zip_file).split('.')[0] + '_BANDINFO.txt'
        out_band_file_path = os.path.join(out_dir, out_band_file_name)
        with open(out_band_file_path, 'w') as f:
            f.write('\n'.join(band_order))

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
    @:param res: 输出分辨率
    @:param temp_dir: 临时目录
    @:param out_dir: 输出文件夹
    """
    # zip_file = r"C:\Users\wangbin\Desktop\S2A\S2A_MSIL1C_20200602T023601_N0209_R089_T51RUQ_20200602T053727.zip"
    # out_dir = r'C:\Users\wangbin\Desktop\S2A\out'
    # temp_dir = r'C:\Users\wangbin\Desktop\S2A\temp'
    # res = 60

    args = sys.argv
    zip_file = args[1]
    out_dir = args[2]
    temp_dir = args[3]

    Sentinel2.main(zip_file, out_dir, temp_dir, 60)
