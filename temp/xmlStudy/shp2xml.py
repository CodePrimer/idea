# -- coding: utf-8 -- 

from lxml import etree
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )

'''福建shp转换为areaCfg,xml'''

xml_fields = ['id','name','level','area','left','right','bottom','top','lon','lat']

def ShpInfo2List(shpPath, fieldList):
    
    shp_list = []
    attribute = arcpy.da.SearchCursor(shpPath, fieldList)
    for a in attribute:
        tuple_id = ('id', unicode(a[0]))
        tuple_name = ('name', unicode(a[1]))
        tuple_level = ('level', unicode(a[2]))
        tuple_area = ('shapeArea', unicode(a[3]))
        tuple_left = ('left', unicode(a[4]))
        tuple_right = ('right', unicode(a[5]))
        tuple_bottom = ('bottom', unicode(a[6]))
        tuple_top = ('top', unicode(a[7]))
        tuple_lon = ('lon', unicode(a[8]))
        tuple_lat = ('lat', unicode(a[9]))
        shp_list.append([tuple_id,tuple_name,tuple_level,tuple_area,tuple_left,tuple_right,tuple_bottom,tuple_top,tuple_lon,tuple_lat])
    return shp_list


def set_node_attrib(node, attr_list):
    attr_obj = node.attrib
    for attr in attr_list:
        attr_obj[attr[0]] = attr[1]
    
    
def deep_search_nodes(root_node, pool):
    
    for each in root_node:
        if len(list(each)) != 0:
            deep_search_nodes(each, pool)
        pool.append(each)
    return pool
  
if __name__ == "__main__":
    
    NationShp = r'C:\Users\wangbin\Desktop\Project\AreaNation.shp'
    ProvinceShp = r'C:\Users\wangbin\Desktop\Project\AreaProvince.shp'
    CityShp = r'C:\Users\wangbin\Desktop\Project\AreaCity.shp'
    CountyShp = r'C:\Users\wangbin\Desktop\Project\AreaCounty.shp'
    XiangShp = r'C:\Users\wangbin\Desktop\Project\AreaXiang.shp'
    

    # 根节点创建
    Fields = ["ID", "NAME", "level", "Area", "XMIN", "XMAX", "YMIN", "YMAX", "XCENTER", "YCENTER"]
    
    
    nation_list = ShpInfo2List(NationShp, Fields)
    row = nation_list[0]
    root_node = etree.Element("region")
    set_node_attrib(root_node, row)
    
    # 二级节点创建
    prov_attr_map = ShpInfo2List(ProvinceShp, Fields)
    for row in prov_attr_map:
        row_node = etree.SubElement(root_node, "province")
        set_node_attrib(row_node, row)
      

    # 三级节点创建
    city_attr_map = ShpInfo2List(CityShp, Fields)
    # 寻找福建省节点
    search_nodes = deep_search_nodes(root_node, [])
    for n in search_nodes:
        if n.attrib["id"] == '350000000000':
            for row in city_attr_map:
                row_node = etree.SubElement(n, "city")
                set_node_attrib(row_node, row)
    
    
    # 四级节点
    count_attr_map = ShpInfo2List(CountyShp, Fields)
    for row in count_attr_map:
        cur_id = row[0][1]
        top_id = cur_id[0:4] + '00000000'
        search_nodes = deep_search_nodes(root_node, [])
        for n in search_nodes:
            if top_id == n.attrib["id"]:
                row_node = etree.SubElement(n, "county")
                set_node_attrib(row_node, row)

    # 五级节点
    xiang_attr_map = ShpInfo2List(XiangShp, Fields)
    for row in xiang_attr_map:
        cur_id = row[0][1]
        top_id = cur_id[0:6] + '000000'
        search_nodes = deep_search_nodes(root_node, [])
        for n in search_nodes:
            if top_id == n.attrib["id"]:
                row_node = etree.SubElement(n, "xiang")
                set_node_attrib(row_node, row)


    doc = etree.ElementTree(root_node)
    doc.write(open(r'C:\Users\wangbin\Desktop\Project\AreaCfg\AreaCfg.xml', "w"), pretty_print=True, encoding = 'UTF-8')
    
    print("Finish")
