from GdalUtil import GdalUtils
import gdal

if __name__ == '__main__':
    in_shp_path = r'E:\Data\temp\New_Shapefile.shp'
    out_tif_path = r'E:\Data\temp\mask2.tif'
    ds = gdal.Open(r'E:\Data\temp\countGT5.tif')
    width = ds.RasterXSize
    height = ds.RasterYSize
    trans = ds.GetGeoTransform()

    leftTopX = trans[0]
    leftTopY = trans[3]
    rightDownX = leftTopX + trans[1] * width
    rightDownY = leftTopY + trans[5] * height
    xMin = min([leftTopX, rightDownX])
    xMax = max([leftTopX, rightDownX])
    yMin = min([leftTopY, rightDownY])
    yMax = max([leftTopY, rightDownY])

    out_bounds = (xMin, yMin, xMax, yMax)
    GdalUtils.PolygonToRaster(in_shp_path, out_tif_path, 10, 10, 'ID', out_bounds=out_bounds)
    print('F')