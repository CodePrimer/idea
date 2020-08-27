# coding=utf-8

from gdalUtils.ShapeFile import ShapeFile
from lxml import etree


def readShpAttr(shpPath, fieldList):

    shpObj = ShapeFile(shpPath)
    attrTable = shpObj.getAttrTable()
    shpInfo = []
    for i in range(attrTable.shape[0]):
        lineInfo = attrTable.loc[i, fieldList]
        tuple_id = ('id', lineInfo[0])
        tuple_name = ('name', lineInfo[1])
        tuple_level = ('level', lineInfo[2])
        tuple_area = ('shapeArea', lineInfo[3])
        tuple_left = ('left', lineInfo[4])
        tuple_right = ('right', lineInfo[5])
        tuple_bottom = ('bottom', lineInfo[6])
        tuple_top = ('top', lineInfo[7])
        tuple_lon = ('lon', lineInfo[8])
        tuple_lat = ('lat', lineInfo[9])
        shpInfo.append([tuple_id,tuple_name,tuple_level,tuple_area,tuple_left,tuple_right,tuple_bottom,tuple_top,tuple_lon,tuple_lat])
    return shpInfo


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

    shpProvince = r"D:\wangbin\htht\HaiNan\CompShp\AreaProvince.shp"
    shpCity = r"D:\wangbin\htht\HaiNan\CompShp\AreaCity.shp"
    shpCounty = r"D:\wangbin\htht\HaiNan\CompShp\AreaCounty.shp"

    fieldList = ["ID", "NAME", "level", "shapeArea", "XMIN", "XMAX", "YMIN", "YMAX", "XCENTER", "YCENTER"]

    provInfo = readShpAttr(shpProvince, fieldList)
    row = provInfo[0]
    root_node = etree.Element("province")
    set_node_attrib(root_node, row)

    # 二级节点创建
    cityInfo = readShpAttr(shpCity, fieldList)
    for row in cityInfo:
        row_node = etree.SubElement(root_node, "city")
        set_node_attrib(row_node, row)

    # 三级节点创建
    countyInfo = readShpAttr(shpCounty, fieldList)
    for row in countyInfo:
        cur_id = row[0][1]
        if cur_id[-1] == ["X"]:
            top_id = cur_id[:-1] + '0'
        else:
            top_id = cur_id[0:4] + '00000000'
        search_nodes = deep_search_nodes(root_node, [])
        for n in search_nodes:
            if top_id == n.attrib["id"]:
                row_node = etree.SubElement(n, "county")
                set_node_attrib(row_node, row)

    doc = etree.ElementTree(root_node)
    doc.write(r'D:\wangbin\htht\HaiNan\AreaCfg.xml', pretty_print=True, encoding='UTF-8')

    print("end")



