from osgeo import ogr
import time

# source_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\CompShp\AreaCounty.shp"
# clip_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\SubShp\530100000000.shp"
# out_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\out\result.shp"

if __name__ == "__main__":

    start_time = time.time()
    shp1 = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\SubShp\530100000000.shp"
    shp2 = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\CompShp\AreaCounty.shp"
    result = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\out\result.shp"

    driver1 = ogr.GetDriverByName('ESRI Shapefile')
    dataSource1 = driver1.Open(shp1, 0)
    layer1 = dataSource1.GetLayer(0)

    driver2 = ogr.GetDriverByName('ESRI Shapefile')
    dataSource2 = driver2.Open(shp2, 0)
    layer2 = dataSource2.GetLayer(0)

    driver3 = ogr.GetDriverByName('ESRI Shapefile')
    datesource3 = driver3.CreateDataSource(result)
    layer3 = datesource3.CreateLayer('layer')
    options = ['SKIP_FAILURES=YES', 'PROMOTE_TO_MULTI=YES', 'INPUT_PREFIX=layer1', 'METHOD_PREFIX=layer2']
    layer2.Clip(layer1, layer3, options=options)

    end_time = time.time()

    print("cost time(s): ", end_time-start_time)

    # start_time = time.time()
    # source_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\CompShp\AreaCounty.shp"
    # clip_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\SubShp\530100000000.shp"
    # out_shp = r"C:\Users\wangbin\Desktop\drivenpage\yunnan_pmd\out\result.shp"
    #
    # source_driven = ogr.GetDriverByName('ESRI Shapefile')
    # source_lyr = source_driven.Open(source_shp, 0).GetLayer(0)
    #
    # clip_driven = ogr.GetDriverByName('ESRI Shapefile')
    # clip_layer = clip_driven.Open(clip_shp, 0).GetLayer(0)
    #
    # out_driven = ogr.GetDriverByName('ESRI Shapefile')
    # out_lyr = out_driven.CreateDataSource(out_shp).CreateLayer('layer')
    # options = ['SKIP_FAILURES=YES', 'PROMOTE_TO_MULTI=YES', 'INPUT_PREFIX=layer1', 'METHOD_PREFIX=layer2']
    # source_lyr.Clip(clip_layer, out_lyr, options=options)
    #
    # end_time = time.time()
    #
    # print("cost time(s): ", end_time-start_time)