# !/usr/bin/python3
# -*- coding: utf-8  -*-

import xml.etree.ElementTree as ET
from TODO.XmlET import XmlET
from collections import OrderedDict


def get_id_list():
    xml_path = r'C:\Users\wangbin\Desktop\AreaCfg.xml'
    tree = XmlET.get_tree(xml_path)
    root_node = XmlET.get_root_node(xml_path)

    all_node = XmlET.search_node(root_node)
    node_id_dict = {}  # id和node对应表
    for each in all_node:
        node_name = XmlET.get_attr(each)['id']
        node_id_dict[node_name] = each

    id_list = sorted(node_id_dict.keys())
    id_list.pop(id_list.index('QHS'))
    return id_list


def get_parent_dict():
    xml_path = r'C:\Users\wangbin\Desktop\AreaCfg.xml'
    tree = XmlET.get_tree(xml_path)

    parend_dict = {}
    for p in tree.iter():
        for c in p:
            c_id = c.attrib['id']
            p_id = p.attrib['id']
            parend_dict[c_id] = p_id
    return parend_dict


if __name__ == '__main__':

    xml_path = r'C:\Users\wangbin\Desktop\AreaCfg.xml'

    id_list = get_id_list()
    parent_dict = get_parent_dict()

    attr_sort = ['id', 'name', 'level', 'lon', 'lat', 'left', 'right', 'top', 'bottom']
    out_root_node = XmlET.create_root_node('province', attr={'id': 'QHS', 'name': '青海省', 'level': '0',
                                                             'lon': '96.235253', 'lat': '35.406628', 'left': '89.40099',
                                                             'right': '103.069516', 'top': '39.212599', 'bottom': '31.600657'})

    tree = ET.parse(xml_path)
    root_node = tree.getroot()

    city_list = []
    county_list = []
    town_list = []
    for i in id_list:
        if i[1:6] == '00000' or i[0] == 'O':
            city_list.append(i)
    for i in id_list:
        if i[3:6] != '000':
            town_list.append(i)

    for i in id_list:
        if i not in city_list and i not in town_list:
            county_list.append(i)

    for i in city_list:
        cur_node = XmlET.search_node(root_node, attr={'id': i})[0]
        attr_dict = OrderedDict()
        for each in attr_sort:
            attr_dict[each] = cur_node.attrib[each]

        tag = XmlET.get_tag(cur_node)
        attr = attr_dict
        text = XmlET.get_text(cur_node)
        node = ET.Element(tag, attr)
        node.text = text
        out_root_node.append(node)

    for i in county_list:
        cur_node = XmlET.search_node(root_node, attr={'id': i})[0]
        attr_dict = OrderedDict()
        for each in attr_sort:
            attr_dict[each] = cur_node.attrib[each]

        tag = XmlET.get_tag(cur_node)
        attr = attr_dict
        text = XmlET.get_text(cur_node)
        node = ET.Element(tag, attr)
        node.text = text
        parent_node = XmlET.search_node(out_root_node, attr={'id': parent_dict[i]})[0]
        parent_node.append(node)

    for i in town_list:
        cur_node = XmlET.search_node(root_node, attr={'id': i})[0]
        attr_dict = OrderedDict()
        for each in attr_sort:
            attr_dict[each] = cur_node.attrib[each]

        tag = XmlET.get_tag(cur_node)
        attr = attr_dict
        text = XmlET.get_text(cur_node)
        node = ET.Element(tag, attr)
        node.text = text
        parent_node = XmlET.search_node(out_root_node, attr={'id': parent_dict[i]})[0]
        parent_node.append(node)

    for i in out_root_node:
        print(i.attrib)

    XmlET.write_xml(out_root_node, r'C:\Users\wangbin\Desktop\AreaCfg2.xml')

    child_nodes = XmlET.get_child_node(root_node)
    for each in child_nodes:
        print(XmlET.get_attr(each))

    # 6.递归查看某标签名节点，iter返回的是生成器
    for each in root.iter('city'):
        print(each.tag)
        print(each.attrib)
        if each.text is None:
            print('')
        else:
            print(each.text.strip())

    # 7.非递归查询某标签名节点，findall返回的是一个列表
    node_list = root.findall('city')
    for each in node_list:
        print(each.tag)
        print(each.attrib)
        if each.text is None:
            print('')
        else:
            print(each.text.strip())

    root.find('city').text = None
    # indent(root, 0)
    tree.write(r'C:\Users\wangbin\Desktop\ProductCfg2.xml', encoding="UTF-8", xml_declaration=True, method='xml')
    print('finish')
