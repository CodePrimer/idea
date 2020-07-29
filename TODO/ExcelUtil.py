# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-

import pandas as pd
import numpy as np


class ExcelUtil(object):
    """
        excelUtil   TODO 待完善
    """

    def __init__(self):
        pass

    @staticmethod
    def pdExportExcel(xlsPath, xlsInfo, sheetSortList=None):
        """
        pandas包to_excel()函数输出EXCEL
        :param xlsPath: excel文件保存路径
        :param xlsInfo: excel文件内容 格式{"sheet1":{"data":dataFrame1, "col":[col1, col2, col3]},
                                          "sheet2":{"data":dataFrame2}, "col":[col1, col2, col3]}
        :param sheetSortList: sheet排序顺序 格式["sheet1", "sheet2"]
        :return:
        """
        # TODO 更多配置参数
        writer = pd.ExcelWriter(xlsPath)
        if sheetSortList:
            for sheet in sheetSortList:
                if sheet in xlsInfo.keys():
                    sheetName = sheet
                    sheetDataFrame = xlsInfo[sheetName]["data"]
                    columns = xlsInfo[sheetName]["col"]
                    sheetDataFrame.to_excel(writer, sheetName, header=True, index=False, columns=columns)
        else:
            for sheet in xlsInfo.keys():
                sheetName = sheet
                sheetDataFrame = xlsInfo[sheetName]["data"]
                columns = xlsInfo[sheetName]["col"]
                sheetDataFrame.to_excel(writer, sheetName, header=True, index=False, columns=columns)
        writer.save()


if __name__ == "__main__":
    df = pd.DataFrame(index=None, columns=["A"])
    xlsInfo = {u"王彬": df}
    sheetSort = [u"王彬"]
    xlsPath = r"C:\Users\wangbin\Desktop\qinghai\test.xls"
    ExcelUtil.pdExportExcel(xlsPath, xlsInfo, sheetSortList=sheetSort)
    print("Finish")

