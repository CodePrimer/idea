import gdal
import os
from GeoTiffFile import GeoTiffFile

"""
    GDAL中矢量转栅格函数Rasterize在使用内存模式时 输出结果异常
    以下为测试代码
"""

if __name__ == '__main__':
    shp_path = r'.\AreaCity.shp'
    print(os.path.isfile(shp_path))
    out_bounds = (89.40099000558433, 31.60065683414564, 103.06951588744829, 39.2125991241503)
    x_res = 0.010477628211129655
    y_res = 0.010477628211129655

    ds = gdal.Rasterize('', shp_path, outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=65535,
                        attribute="obj_id", useZ=False, xRes=x_res, yRes=y_res, format="MEM")

    # out_path = r'C:\Users\wangbin\Desktop\statistic\temp\rasterize.tif'
    # ds = gdal.Rasterize(out_path, shp_path, outputBounds=out_bounds, outputType=gdal.GDT_UInt16, noData=65535,
    #                     attribute="obj_id", useZ=False, xRes=x_res, yRes=y_res, format="GTiff")

    arr = ds.GetRasterBand(1).ReadAsArray()

    in_tif = GeoTiffFile(r'.\rasterize.tif')
    in_tif.readTif()
    out_tif = GeoTiffFile(r'.\rasterize2.tif')
    out_tif.setData(arr)
    out_tif.setProj(in_tif.getProj())
    out_tif.setGeoTrans(in_tif.getGeoTrans())
    out_tif.setDims(in_tif.getWidth(), in_tif.getHeight(), in_tif.getBands())
    out_tif.writeTif()

    print('finish')