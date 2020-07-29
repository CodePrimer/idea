# !/usr/bin/python3
# -*- coding: utf-8  -*-

import pandas as pd

"""使用pandas实现类似sql语句"""


if __name__ == '__main__':

    """
        首先对比一下pandas和mysql的数据类型：
        
        1.pandas数据类型：
            字符串类型：object
            整数类型：Int64，Int32，Int16, Int8 
            无符号整数：UInt64，UInt32，UInt16, UInt8 
            浮点数类型：float64，float32
            日期和时间类型：datetime64[ns]、datetime64[ns, tz]、timedelta[ns]
            布尔类型：bool
        
        2.mysql数据类型：
            大致可以分为四类：数值型、浮点型、日期/时间和字符串(字符)类型，具体不详细介绍
    
    测试数据
    1.Test DataFrame.csv
    2.Test DataFrame.xlsx
        
    """

    # 读取excel可以保留excel原有的列类型
    # csv为纯文本格式文件，读取后所有列都为字符串类型
    xlsx_path = r'.\Test DataFrame.xlsx'
    csv_path = r'.\Test DataFrame.csv'
    df_xlsx = pd.read_excel(xlsx_path, sheet_name=0, header=0)
    df_csv = pd.read_csv(csv_path, header=0)
    print(df_xlsx['Date'].dtype)
    print(df_csv['Date'].dtype)

    # 数据类型转换
    # 1.将整型列数据转换为字符串
    a = df_xlsx['Orders'].astype(str)
    # 2.将浮点型列数据转换为字符串
    b = df_xlsx['Demand(USD)'].astype(str)
    # 3.将字符串数据转换为浮点型
    c = df_xlsx['Demand_str'].astype(float)
    # 4.将字符串数据转换为整型，精度丢失
    d = df_xlsx['Demand_str'].astype(int)

    # 时间格式创建，时间格式本质为时间戳，能进行大小对比
    date_time1 = pd.to_datetime('2019-07-01 00:00:00')
    date_time2 = pd.to_datetime('2019-07-01')

    # =================================================================================== #
    # 查询DataFrame的所有列名
    column_list = df_xlsx.columns.to_list()
    print(column_list)

    # 数据库查询操作
    # 1.查询某表中某列
    # select ID from df_xlsx
    result1 = df_xlsx['ID']

    # 2.查询某表中的某几列
    # select ID,Date,ProductName from df_xlsx
    result2 = df_xlsx[['ID', 'Date', 'ProductName']]

    # 3.查询某列等于某值的所有列
    # select * from df_xlsx where ID = '167749C281'
    result3 = df_xlsx[df_xlsx['ID'] == '167749C281']

    # 4.查询某列等于某值的某几列
    # select ID,Date,ProductName from df_xlsx where ProductName = 'CHUCK 7NULL'
    result5 = df_xlsx[['ID', 'Date', 'ProductName']][df_xlsx['ProductName'] == 'CHUCK 7NULL']

    # 5.查询某列不等于某值
    # select * from df_xlsx where ID != '167749C281'
    result6 = df_xlsx[df_xlsx['ID'] != '167749C281']

    # 6.多条件查询
    # 且 &
    # select * from df_xlsx where ProductName = 'CHUCK 7NULL' and Demand(USD) < 400'
    result7 = df_xlsx[(df_xlsx['ProductName'] == 'CHUCK 7NULL') & (df_xlsx['Demand(USD)'] < 400)]
    # 或 |
    result8 = df_xlsx[(df_xlsx['ProductName'] == 'CHUCK 7NULL') | (df_xlsx['Demand(USD)'] < 400)]

    # 7.查询某列符合某个列表的情况
    # select * from df_xlsx where ProductName in ('CHUCK 7NULL', 'CONVERSE X')
    result9 = df_xlsx[df_xlsx['ProductName'].isin(['CHUCK 7NULL', 'CONVERSE X'])]

    # 8.查询某列不符合某个列表的情况
    # select * from df_xlsx where ProductName not in ('CHUCK 7NULL', 'CONVERSE X')
    result10 = df_xlsx[~df_xlsx['ProductName'].isin(['CHUCK 7NULL', 'CONVERSE X'])]

    # 9.模糊匹配
    """
    使用str.contains()函数匹配字符串
    参数:
        Series.str.contains(pat, case=True, flags=0, na=nan, regex=True)是否包含查找的字符串
        pat : 字符串/正则表达式
        case : 布尔值, 默认为True.如果为True则匹配敏感
        flags : 整型,默认为0(没有flags)
        na : 默认为NaN,替换缺失值.
        regex : 布尔值, 默认为True.如果为真则使用re.research,否则使用Python
    返回值:
        布尔值的序列(series)或数组(array)
    """
    # select * from df_xlsx where ProductName like 'CT%'
    """
    原始数据中字符串NULL会在读取时默认转换为numpy的nan
    进行str.contains后会保留nan属性而不转换为True/False 导致选择子集失败
    加入关键字na=False可以将NULL值筛选掉
    """
    result11 = df_xlsx[df_xlsx['ProductName'].str.contains('CT', na=False)]
    result12 = df_xlsx[~df_xlsx['ID'].str.contains('167')]

    # 正则匹配
    # ProductName以C开头X结尾
    result13 = df_xlsx['ProductName'][df_xlsx['ProductName'].str.contains('C*X', na=False)]

    print('Finish')
