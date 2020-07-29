# -*- coding: UTF-8 -*-
import pandas as pd
import re


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


def test():
    """提取客户对话内容"""

    # 文件路径
    file_path = r'C:\Users\Think\Desktop\may test.xls'
    excel_data = pd.read_excel(file_path)
    data = excel_data[['session id', 'content']]  # 获取content列

    for index, row_data in data.iterrows():
        session_id = str(row_data.to_list()[0])
        content = str(row_data.to_list()[1])

        # 如果第二列内容空白则跳过
        if content == 'nan':
            continue

        if session_id == '121319':
            print('aaa')

        # 先打印原内容，以便调试
        print("=" * 50)
        print("session_id:", session_id)
        print(content)
        print("*" * 50)

        # 字符串去除以下内容:
        # （1）“对话开始yyyy-MM-dd HH:mm:ss”
        # （2）“对话结束yyyy-MM-dd HH:mm:ss”
        # （3）“系统 yyyy-MM-dd HH:mm:ss
        #       ——以下是排队消息记录——”

        del_str_pattern1 = re.compile("对话开始[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]")
        del_str_pattern2 = re.compile("对话结束[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]")
        del_str_pattern3 = re.compile(
            "系统 [0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\r\n——以下是排队消息记录——")
        if len(del_str_pattern1.findall(content)) > 0:
            del_str1 = del_str_pattern1.findall(content)[0]
            content = content.replace(del_str1, '')
        if len(del_str_pattern2.findall(content)) > 0:
            del_str2 = del_str_pattern2.findall(content)[0]
            content = content.replace(del_str2, '')
        if len(del_str_pattern3.findall(content)) > 0:
            del_str3 = del_str_pattern3.findall(content)[0]
            content = content.replace(del_str3, '')
        # 打印处理后数据
        print(content)

        # 获取用户名称
        content_list = content.split('\n')
        # 过滤空行
        content_list_new = []
        for each in content_list:
            if each.strip() != "":
                content_list_new.append(each)

        print("#" * 50)
        first_line = content_list_new[0].strip()
        user_name = first_line.split(' ')[0]  # 去除前后空格后的用户名
        print(user_name)  # 打印用户名

        # 寻找用户名抬头下一行内容即为用户聊天
        for i in range(len(content_list_new)):
            cur_context = content_list_new[i].strip()
            if cur_context.startswith(user_name):
                print(content_list_new[i + 1])  # 打印客户语句
    print('finish')


if __name__ == '__main__':

    """提取客户对话内容"""

    # 文件路径
    file_path = r'C:\Users\Think\Desktop\may test.xls'
    excel_data = pd.read_excel(file_path)
    data = excel_data[['session id', 'content']]  # 获取content列

    # 创建结果dataframe
    result_id = []
    result_user_name = []
    result_context = []

    for index, row_data in data.iterrows():
        session_id = str(row_data.to_list()[0])
        content = str(row_data.to_list()[1])

        # 如果第二列内容空白则跳过
        if content == 'nan':
            continue

        # # 先打印原内容，以便调试
        # print("=" * 50)
        # print("session_id:", session_id)
        # print(content)
        # print("*" * 50)

        # 字符串去除以下内容:
        # （1）“对话开始yyyy-MM-dd HH:mm:ss”
        # （2）“对话结束yyyy-MM-dd HH:mm:ss”
        # （3）“系统 yyyy-MM-dd HH:mm:ss
        #       ——以下是排队消息记录——”

        del_str_pattern1 = re.compile("对话开始[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]")
        del_str_pattern2 = re.compile("对话结束[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]")
        del_str_pattern3 = re.compile(
            "系统 [0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\r\n——以下是排队消息记录——")
        if len(del_str_pattern1.findall(content)) > 0:
            del_str1 = del_str_pattern1.findall(content)[0]
            content = content.replace(del_str1, '')
        if len(del_str_pattern2.findall(content)) > 0:
            del_str2 = del_str_pattern2.findall(content)[0]
            content = content.replace(del_str2, '')
        if len(del_str_pattern3.findall(content)) > 0:
            del_str3 = del_str_pattern3.findall(content)[0]
            content = content.replace(del_str3, '')
        # # 打印处理后数据
        # print(content)

        # 获取用户名称
        content_list = content.split('\n')
        # 过滤空行
        content_list_new = []
        for each in content_list:
            if each.strip() != "":
                content_list_new.append(each)

        # print("#" * 50)
        first_line = content_list_new[0].strip()
        user_name = first_line.split(' ')[0]  # 去除前后空格后的用户名
        # print(user_name)  # 打印用户名

        # 寻找用户名抬头下一行内容即为用户聊天
        for i in range(len(content_list_new)):
            cur_context = content_list_new[i].strip()
            if cur_context.startswith(user_name):
                result_id.append(session_id)
                result_user_name.append(user_name)
                result_context.append(content_list_new[i + 1])
                # print(session_id)
                # print(user_name)  # 打印用户名
                # print(content_list_new[i + 1])  # 打印客户语句
    result_df = pd.DataFrame({'session': result_id, 'username': result_user_name, 'context': result_context})
    xlsInfo = {'sheet1': {"data": result_df, "col": ['session', 'username', 'context']}}
    out_excel = r'C:\Users\Think\Desktop\result.xlsx'
    pdExportExcel(out_excel, xlsInfo)
    print('finish')

