from XmlUtil import XmlUtil
import xml.dom.minidom

if __name__ == '__main__':
    xml_path = r"C:\Users\wangbin\Desktop\utils\AreaCfg.xml"
    dom = xml.dom.minidom.parse(xml_path)
    root_node = dom.documentElement
    city_nodes = root_node.getElementsByTagName('city')
    for city_node in city_nodes:
        node_attr = XmlUtil.get_node_attr(city_node)
        county_nodes = city_node.getElementsByTagName('county')
        for county_node in county_nodes:
            node_attr = XmlUtil.get_node_attr(root_node)
            lat = node_attr["lon"]
            lon = node_attr["lat"]
            county_node.setAttribute("lon", lon)
            county_node.setAttribute("lat", lat)
    with open(r"C:\Users\wangbin\Desktop\utils\AreaCfg1.xml", 'w', encoding='utf-8') as f:
        dom.writexml(f, encoding='utf-8')
    print("Finish")
