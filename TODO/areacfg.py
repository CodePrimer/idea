from ShapeFile import ShapeFile
from XmlUtil import XmlUtil

"""根据shp文件生成AreaCfg.xml文件"""

if __name__ == "__main__":

    province_shp = r"C:\Users\wangbin\Desktop\yunnan2\code\depend\shp\CompShp\AreaProvince.shp"
    city_shp = r"C:\Users\wangbin\Desktop\yunnan2\code\depend\shp\CompShp\AreaCity.shp"
    county_shp = r"C:\Users\wangbin\Desktop\yunnan2\code\depend\shp\CompShp\AreaCounty.shp"

    dom = XmlUtil.createDom()
    # 读取省矢量
    province_obj = ShapeFile(province_shp)
    province_obj.readShp()
    attr_table = province_obj.getAttrTable()
    sql_id = "530000000000"
    id = attr_table.loc[attr_table["ID"] == sql_id]["ID"].to_list()[0]
    name = attr_table.loc[attr_table["ID"] == sql_id]["NAME"].to_list()[0]
    level = attr_table.loc[attr_table["ID"] == sql_id]["LEVEL"].to_list()[0]
    left = attr_table.loc[attr_table["ID"] == sql_id]["XMIN"].to_list()[0]
    right = attr_table.loc[attr_table["ID"] == sql_id]["XMAX"].to_list()[0]
    bottom = attr_table.loc[attr_table["ID"] == sql_id]["YMIN"].to_list()[0]
    top = attr_table.loc[attr_table["ID"] == sql_id]["YMAX"].to_list()[0]
    lat = attr_table.loc[attr_table["ID"] == sql_id]["YCENTER"].to_list()[0]
    lon = attr_table.loc[attr_table["ID"] == sql_id]["XCENTER"].to_list()[0]
    attr = {"id": id, "name": name, "level": level,  "left": left, "right": right,
            "bottom": bottom, "top": top, "lat": lat, "lon": lon}
    root_node = XmlUtil.createRootNode(dom, "province", attrInfo=attr)

    # 读取市矢量
    city_obj = ShapeFile(city_shp)
    city_obj.readShp()
    attr_table = city_obj.getAttrTable()
    city_node_dict = {}
    for city in attr_table["ID"].to_list():
        sql_id = city
        id = attr_table.loc[attr_table["ID"] == sql_id]["ID"].to_list()[0]
        name = attr_table.loc[attr_table["ID"] == sql_id]["NAME"].to_list()[0]
        level = attr_table.loc[attr_table["ID"] == sql_id]["LEVEL"].to_list()[0]
        left = attr_table.loc[attr_table["ID"] == sql_id]["XMIN"].to_list()[0]
        right = attr_table.loc[attr_table["ID"] == sql_id]["XMAX"].to_list()[0]
        bottom = attr_table.loc[attr_table["ID"] == sql_id]["YMIN"].to_list()[0]
        top = attr_table.loc[attr_table["ID"] == sql_id]["YMAX"].to_list()[0]
        lat = attr_table.loc[attr_table["ID"] == sql_id]["YCENTER"].to_list()[0]
        lon = attr_table.loc[attr_table["ID"] == sql_id]["XCENTER"].to_list()[0]
        attr = {"id": id, "name": name, "level": level, "left": left, "right": right,
                "bottom": bottom, "top": top, "lat": lat, "lon": lon}
        cur_city_node = XmlUtil.appendNode(dom, root_node, "city", attrInfo=attr)
        city_node_dict[city] = cur_city_node

    # 读取县矢量
    county_obj = ShapeFile(county_shp)
    county_obj.readShp()
    attr_table = county_obj.getAttrTable()
    for county in attr_table["ID"].to_list():
        sql_id = county
        parent_id = county[0:4] + "00000000"
        id = attr_table.loc[attr_table["ID"] == sql_id]["ID"].to_list()[0]
        name = attr_table.loc[attr_table["ID"] == sql_id]["NAME"].to_list()[0]
        level = attr_table.loc[attr_table["ID"] == sql_id]["LEVEL"].to_list()[0]
        left = attr_table.loc[attr_table["ID"] == sql_id]["XMIN"].to_list()[0]
        right = attr_table.loc[attr_table["ID"] == sql_id]["XMAX"].to_list()[0]
        bottom = attr_table.loc[attr_table["ID"] == sql_id]["YMIN"].to_list()[0]
        top = attr_table.loc[attr_table["ID"] == sql_id]["YMAX"].to_list()[0]
        lat = attr_table.loc[attr_table["ID"] == sql_id]["YCENTER"].to_list()[0]
        lon = attr_table.loc[attr_table["ID"] == sql_id]["XCENTER"].to_list()[0]
        attr = {"id": id, "name": name, "level": level, "left": left, "right": right,
                "bottom": bottom, "top": top, "lat": lat, "lon": lon}
        parent_node = city_node_dict[parent_id]
        XmlUtil.appendNode(dom, parent_node, "county", attrInfo=attr)

    save_path = r"C:\Users\wangbin\Desktop\piemapping\AreaCfg.xml"
    XmlUtil.saveDom(dom, save_path)