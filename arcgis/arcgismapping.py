# -*-- coding: UTF-8 -*-

import arcpy
import os
import re
import pickle
import sys
import time


def export_pic(mxd_path, out_path, replace_lyr, replace_text, drivenpage, dpi, out_type):
    """
    arcmap出图函数
    :param mxd_path: str: mxd模板路径
    :param out_path: str: 输出专题图路径，DrivenPage形式出图路径，用{}标识DrivenPage属性字段  e.g: 'C:/User/Desktop/{id}/abc_{id}_def.png'
    :param replace_lyr: dict: 替换破损图层字典  e.g: {'mxd中破损图层名': '替换数据源绝对路径'}
    :param replace_text: dict: 替换文本字典   e.g: {'mxd中文本元素名': {'替换前文本': '替换后文本'} }
    :param drivenpage: bool: 是否以DrivenPage形式出图，默认不以DrivenPage形式出图
    :param dpi: int: 出图分辨率
    :param out_type: str: 图片类型  目前支持.jpg/.png
    :return:
    """
    replace_lyr_info = {}
    for each in replace_lyr.keys():
        source_dir = os.path.dirname(replace_lyr[each])
        source_basename = os.path.basename(replace_lyr[each])
        (source_file_name, source_file_ext) = os.path.splitext(source_basename)
        replace_lyr_info[each] = {'dir': source_dir, 'name': source_file_name, 'ext': source_file_ext}

    mxd = arcpy.mapping.MapDocument(mxd_path)

    # 替换图层
    for lyr in arcpy.mapping.ListBrokenDataSources(mxd):
        if str(lyr) not in replace_lyr_info.keys():
            continue
        workspace = replace_lyr_info[str(lyr)]["dir"]
        filename = replace_lyr_info[str(lyr)]["name"]
        if replace_lyr_info[str(lyr)]["ext"] == ".shp":
            lyr.replaceDataSource(workspace, "SHAPEFILE_WORKSPACE", filename)
        if replace_lyr_info[str(lyr)]["ext"] in [".tif", ".dat"]:
            lyr.replaceDataSource(workspace, "RASTER_WORKSPACE", filename)

    # 替换文本
    for textElement in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
        if textElement.name in replace_text.keys():
            replace_content = replace_text[textElement.name]
            text = textElement.text
            for each in replace_content.keys():
                replace_val = replace_content[each]
                text = text.replace(each, replace_val)
                textElement.text = text

    # 判断是否驱动页出图
    if not drivenpage:
        out_dir = os.path.dirname(out_path)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        if out_type.upper() == '.JPG':
            arcpy.mapping.ExportToJPEG(mxd, out_path, resolution=dpi)
        elif out_type.upper() == '.PNG':
            arcpy.mapping.ExportToPNG(mxd, out_path, resolution=dpi)
        else:
            pass
    else:
        for page_num in range(1, mxd.dataDrivenPages.pageCount + 1):
            print('DrivenPage Processing ' + str(page_num) + "/" + str(mxd.dataDrivenPages.pageCount))
            mxd.dataDrivenPages.currentPageID = page_num
            # 正则匹配大括号对{}
            regex = re.compile(r'\{.*?\}')
            replace_list = regex.findall(out_path)
            if len(replace_list) == 0:
                print('"out_path" ValueError when choose drivenpage mode.')
                return
            cur_out_dir = os.path.dirname(out_path)
            cur_out_name = os.path.basename(out_path)
            for field in replace_list:
                field_name = field[1:-1]
                try:
                    field_value = str(mxd.dataDrivenPages.pageRow.getValue(field_name))
                    cur_out_dir = cur_out_dir.replace(field, field_value)
                    cur_out_name = cur_out_name.replace(field, field_value)
                except ValueError:
                    print('Cannot find ' + field_name + ' in drivenpage shapefile')
                    return
            if not os.path.isdir(cur_out_dir):
                os.makedirs(cur_out_dir)
            cur_out_path = os.path.join(cur_out_dir, cur_out_name)
            if out_type.upper() == '.JPG':
                arcpy.mapping.ExportToJPEG(mxd, cur_out_path, resolution=dpi)
            elif out_type.upper() == '.PNG':
                arcpy.mapping.ExportToPNG(mxd, cur_out_path, resolution=dpi)
            else:
                pass


def main(args):
    # 读取pkl变量
    fr = open(args[1], 'rb')
    param = pickle.load(fr)
    fr.close()
    mxdPath = param['mxdPath']
    outPath = param['outPath']
    replaceLyr = param['replaceLyr']
    replaceText = param['replaceText']
    drivenPage = param['drivenPage']
    dpi = param['dpi']
    outType = param['outType']

    export_pic(mxdPath, outPath, replaceLyr, replaceText, drivenPage, dpi, outType)


if __name__ == '__main__':

    main(sys.argv)

    # mxdPath = r'C:\Users\wangbin\Desktop\drivenpage\arcpy\EVI_.mxd'
    # outPath = r'C:\Users\wangbin\Desktop\drivenpage\arcpy\outpic\test_{id}.png'
    # replaceLyr = {"tifFile": r'C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\tif\EVI.tif'}
    # replaceText = {"date": {"date": '20200509'}, "info": {"satellite": "sat", "sensor": "sen", "resolution": '100'}}
    # drivenPage = True
    # dpi = 300
    # outType = '.png'

    # mxdPath = r'C:\Users\wangbin\Desktop\drivenpage\arcpy\EVI_.mxd'
    # outPath = r'C:\Users\wangbin\Desktop\drivenpage\arcpy\outpic\test123.png'
    # replaceLyr = {"tifFile": r'C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\tif\EVI.tif'}
    # replaceText = {"date": {"date": '20200509'}, "info": {"satellite": "sat", "sensor": "sen", "resolution": '100'}}
    # drivenPage = False
    # dpi = 300
    # outType = '.png'
    #
    # start_time = time.time()
    # export_pic(mxdPath, outPath, replaceLyr, replaceText, drivenPage, dpi, outType)
    # end_time = time.time()
    # print(end_time - start_time)


