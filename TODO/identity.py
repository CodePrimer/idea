import ogr
import osr
import gdal

# 实现ArcToolBox - Analysis Tools - Overlay - Identity


if __name__ == '__main__':

    

    shp1 = r'C:\Users\wangbin\Desktop\yunnan3\code\depend\shp\CompShp\AreaCity.shp'
    shp2 = r'C:\Users\wangbin\Desktop\yunnan3\code\depend\shp\water\HYDA.shp'

    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")  # 为了支持中文路径，请添加
    gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")  # 为了使属性表字段支持中文，请添加
    ogr.RegisterAll()  # 注册所有的驱动
    driver = ogr.GetDriverByName("ESRI Shapefile")  # 数据格式的驱动

    # 打开第一个shp获取图层数据
    ds1 = driver.Open(shp1)
    layer1 = ds1.GetLayer(0)

    # 打开第二个shp获取图层数据
    ds2 = driver.Open(shp2)
    layer2 = ds2.GetLayer(0)

    # 创建结果文件
    save_shp_path = r"C:\Users\wangbin\Desktop\yunnanData\tempdir\TestPolygon.shp"
    oDS = driver.CreateDataSource(save_shp_path)
    # 创建坐标投影对象
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    # 创建结果图层
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon)
    layer2.Identity(layer1, oLayer)
    # 计算多边形面积

    for feature in oLayer:
        id = feature.GetField('ID')
        print(id)
        geom = feature.GetGeometryRef()
        area = geom.GetArea()
        m_area = (area/(0.0089**2))  # 单位平方千米
        print(m_area)
