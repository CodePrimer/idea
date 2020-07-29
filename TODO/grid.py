import gdal
import ogr
import osr
import pandas as pd
from GdalUtil import Grid


def txt2shp(in_txt, out_shp, field_name):

    # 生成shp
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    ogr.RegisterAll()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.CreateDataSource(out_shp)

    # 创建shp的坐标系
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = ds.CreateLayer("PointLayer", srs, ogr.wkbPoint)

    # 创建属性表字段
    field_value = ogr.FieldDefn(field_name, ogr.OFTReal)
    # 对layer对象添加字段
    layer.CreateField(field_value)

    # 打开txt按行创建feature
    with open(in_txt, 'r') as f:
        header = f.readline()
        for line in f.readlines():
            line_content = line.strip('\n')
            lat = line_content.split(' ')[0]
            lon = line_content.split(' ')[1]
            tem_avg = line_content.split(' ')[2]

            # 创建feature
            feature = ogr.Feature(layer.GetLayerDefn())
            # 设置feature属性值
            feature.SetField(field_name, tem_avg)
            # 编辑该feature的wkt字符串
            wkt = 'POINT({0} {1})'.format(lon, lat)
            # 根据wkt创建feature
            feature.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
            # 将feature添加到layer中
            layer.CreateFeature(feature)


if __name__ == '__main__':

    txt_path = r'C:\Users\wangbin\Desktop\cimiss\20101231000000\SURF_CHN_MUL_TEN_20101231.txt'
    data = pd.read_csv(txt_path, sep=' ')
    sql_list = ['Lat', 'Lon', 'TEM_Avg', 'PRE_Time_2020', 'SSH']
    sql_result = data[sql_list][(data['Mon'] == 1) & (data['TEN'] == 1)]

    txt_path = r'C:\Users\wangbin\Desktop\cimiss\temp\result.txt'
    sql_result.to_csv(txt_path, sep=' ', index=False)

    shp_path = r'C:\Users\wangbin\Desktop\cimiss\temp\tem.shp'
    field_name = 'value'
    txt2shp(txt_path, shp_path, field_name)

    out_tif_path = r'C:\Users\wangbin\Desktop\cimiss\temp\tem.tif'
    Grid.invdist(shp_path, out_tif_path, field_name)

    print('finish')
