# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-

import os
import shutil


class BaseUtil(object):
    """基础操作类"""

    def __init__(self):
        pass

    @staticmethod
    def get_filter_file(dir_path, func=None):
        """
         返回文件夹路径下的所有文件路径（搜索文件夹中的文件夹）
         传入方法对文件路径进行过滤
        :param dir_path: str 文件夹路径
        :param func: 用于筛选路径的方法  e.g lambda x: str(x).endswith('Pro4.tif')
        :return:
        """
        # 【1】判断输入参数
        if not os.path.isdir(dir_path):
            print(" 不是文件夹路径 ")
            raise EOFError

        result_path = []
        for i, j, k in os.walk(dir_path):
            for each in k:
                abs_path = i + os.sep + each
                if func is None:  # is 判断是不是指向同一个东西
                    result_path.append(abs_path)
                else:
                    # 使用自定义方法对文件进行过滤
                    if func(abs_path):
                        result_path.append(i + os.sep + each)
        return result_path

    @staticmethod
    def file_size(file_path, unit="B"):
        """
        返回当前文件的大小
        :param file_path: str: 文件路径
        :param unit: str: 返回单位
        :return: float: 文件大小 默认单位为B
        """
        size_byte = os.path.getsize(file_path)
        unit_factor = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        return size_byte / unit_factor[unit.upper()]

    @staticmethod
    def file_path_info(file_path):
        """
        获取文件路径，文件名(无后缀)，文件扩展名
        :param file_path: str: 文件路径 # TODO 文件夹路径如何过滤
        :return:list
        """
        file_dir = os.path.dirname(file_path)
        file_name = BaseUtil.file_name(file_path, ext=False)
        file_ext = BaseUtil.file_ext(file_path)
        return [file_dir, file_name, file_ext]

    @staticmethod
    def file_name(file_path, ext=True):
        """
        获取文件名
        :param file_path: str: 文件路径 # TODO 文件夹路径如何过滤
        :param ext: bool: True-返回值带文件类型 False-返回值不带文件类型
        :return: str
        """
        base_name = os.path.basename(file_path)
        if not ext:     # TODO 没后缀名文件有问题
            split_list = base_name.split(".")
            split_list.pop()
            return ".".join(split_list)
        else:
            return base_name

    @staticmethod
    def file_ext(file_path):
        """
        获取文件扩展类型
        :param file_path: str: 文件路径
        :return:str
        """
        try:
            ext = os.path.splitext(file_path)[1]
            return ext
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def list_file(dir_path, ext=None):
        """
        遍历文件夹内文件
        :param dir_path: str: 文件夹路径
        :param ext: str: 指定扩展名（默认不指定） example: ext=".txt"
        :return:list
        """
        f_list = []
        if not ext:
            for f in os.listdir(dir_path):
                f_list.append(os.path.join(dir_path, f))
        else:
            for f in os.listdir(dir_path):
                if BaseUtil.file_ext(f) == ext:
                    f_list.append(os.path.join(dir_path, f))
        return f_list

    @staticmethod
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

    @staticmethod
    def file_rename(source_file, new_name):
        """
        只限文件改名，限制复制功能
        :param source_file: str: 被改名文件绝对路径
        :param new_name: str: 新文件名 （不包含文件路径）
        :return: True - 执行成功 False - 执行失败
        """
        try:
            if not os.path.isfile(source_file):
                print("重命名文件不存在")
                return False
            file_path = os.path.dirname(source_file)
            new_file_path = os.path.join(file_path, new_name)
            os.rename(source_file, new_file_path)
        except Exception as e:
            print(e)

    @staticmethod
    def is_file(file_path):
        """
        文件存在检测
        :param file_path: 检测文件路径
        :return: True - 是文件 False - 不是文件
        """
        if not isinstance(file_path, str):
            return False
        if os.path.isfile(file_path):
            return True
        else:
            return False

    @staticmethod
    def is_dir(dir_path):
        """
        文件夹存在检测
        :param dir_path: 检测文件夹路径
        :return: True - 是文件夹 False - 不是文件夹
        """
        if not isinstance(dir_path, str):
            return False
        if os.path.isdir(dir_path):
            return True
        else:
            return False

    @staticmethod
    def create_dir(dir_path):
        """
        创建文件夹
        :param dir_path: 创建文件夹路径
        :return: True - 创建成功 False - 创建失败
        """
        try:
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            return True
        except Exception as e:
            print(e)
            return False

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


if __name__ == "__main__":

    test_dir_path = r"E:\Code\QingHai\Production\MOD09GQ\202002"
    result_file = BaseUtil.get_filter_file(test_dir_path, lambda x: str(x).endswith('Pro4.tif'))
    print(result_file)

    print("finish")
