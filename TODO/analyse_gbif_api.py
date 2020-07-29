from BaseUtil import BaseUtil
from urllib import request
import pandas as pd


"""使用request包通过接口方式下载病虫害数据"""

def download_data(start_offset, out_txt):
    # start_offset = 6000
    # out_txt = r'C:\Users\wangbin\Desktop\bch\result300_350page.txt'

    table_head = ['scientificName', 'year', 'month', 'day', 'decimalLongitude', 'decimalLatitude']
    with open(out_txt, 'w') as f:
        # 写表头
        f.write('\t'.join(table_head) + '\n')

        for i in range(50):
            offset = start_offset + 20 * i
            print(offset)
            url = r"https://www.gbif.org/api/occurrence/search?advanced=false&locale=en&offset=" + str(offset) + "&taxon_key=8352161"

            req = request.Request(url)
            req.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36')

            with request.urlopen(url) as r:
                data = r.read()
                print("Status:", r.status, r.reason)
                html_text = data.decode("utf-8")

            # 转换为python的字典结构
            html_text = html_text.replace("false", "False")
            null = 'null'
            html_text_dict = eval(html_text)

            # 获取results信息
            results_list = html_text_dict['results']

            table_head = ['scientificName', 'year', 'month', 'day', 'decimalLongitude', 'decimalLatitude']

            for each in results_list:
                data_list = []
                for h in table_head:
                    if h not in each.keys():
                        data_list.append("Null")
                    else:
                        data_list.append(str(each[h]))
                f.write('\t'.join(data_list) + '\n')


if __name__ == '__main__':

    # 创建一个空的DataFrame
    df = pd.DataFrame(columns=('name', 'year', 'month', 'day', 'longitude', 'latitude'))
    i = 0

    # 读取数据
    dir_path = r'C:\Users\wangbin\Desktop\bch'
    file_list = BaseUtil.list_file(dir_path, ext='.txt')

    for file in file_list:
        with open(file, 'r') as f:
            # 跳过第一行
            f.readline()
            for each_line in f:
                line_content_list = each_line.strip().split('\t')
                df.loc[i] = line_content_list
                i += 1

    # 清洗数据
    # 查询DataFrame的所有列名
    column_list = df.columns.to_list()
    # 查询某列的唯一值
    uni_value = list(df['name'].unique())
    # 查询某列等于某值
    # select * from df where name = 'Spodoptera exigua (Hubner, 1808)'
    sql_name = 'Spodoptera exigua (Hubner, 1808)'
    sql_result1 = df[df['name'] == sql_name]

    # 若要控制返回列则可以这么写
    # 一列的情况
    # select name from df where name = 'Spodoptera exigua (Hubner, 1808)'
    sql_result2 = df['name'][df['name'] == sql_name]
    # 或者
    # sql_result2 = df[['name']][df['name'] == sql_name]
    # 多列的情况
    # select name,year from df where name = 'Spodoptera exigua (Hubner, 1808)'
    sql_result3 = df[['name', 'year']][df['name'] == sql_name]

    # 查询某列等于多个值的情况
    sql_list = ['Spodoptera exigua (Hubner, 1808)', 'Laphygma exigua (Hübner, 1808)']
    sql_result4 = df['name'][df['name'].isin(sql_list)]

    # 查询某列不等于某值
    sql_result5 = df['name'][df['name'] != 'Spodoptera exigua (Hubner, 1808)']

    # 综合查询
    # &条件与
    # |条件或
    sql_result6 = df[(df['name'].isin(sql_list)) &
                     (df['month'] != 'Null') &
                     (df['day'] != 'Null') &
                     (df['longitude'] != 'Null') &
                     (df['latitude'] != 'Null')]

    out_csv = r'C:\Users\wangbin\Desktop\bch\result_sql.txt'
    sql_result6.to_csv(out_csv, encoding="utf-8", index=None)
    print('finish')
