# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-

import xml.etree.ElementTree as ET

"""
    使用xml.etree包实现对xml文件操作
    
"""


class XmlET(object):

    @staticmethod
    def get_tree(xml_path):
        tree = ET.parse(xml_path)
        return tree

    @staticmethod
    def get_root_node(xml_path):
        """
        返回根节点
        :param xml_path: str: xml文件路径
        :return:
        """
        tree = ET.parse(xml_path)
        root_node = tree.getroot()
        return root_node

    @staticmethod
    def get_child_node(node):
        """
        获取某节点的所有子节点列表     TODO 这方法比较蠢，因为node本来就是个迭代器，所以只是为了获取返回的子节点列表
        :param node: Element: 被查询节点
        :return:
        """
        node_list = []
        for each in node:
            node_list.append(each)
        return node_list

    @staticmethod
    def get_parent_dict(tree):
        """
        获取父子节点对应关系字典
        :param tree: 树结构
        :return: dict: 父子节点关系字典
        """
        parend_dict = {}
        for p in tree.iter():
            for c in p:
                parend_dict[c] = p
        return parend_dict

    @staticmethod
    def search_node(node, tag=None, attr=None, text=None):
        """
        在某节点下递归查询符合条件的节点
        :param node: Element: 被查询节点
        :param tag: str: 查询条件标签名
        :param attr: dict: 查询条件属性值 e.g {'name': 'xml', 'id': '123'}
        :param text: str: 查询条件文本
        :return:
        """
        node_list = []

        for each in node.iter():
            each_tag = each.tag
            each_attr = each.attrib
            if each.text is not None:
                each_text = each.text.strip()
            else:
                each_text = ''

            # 初始化判断标识
            flag_tag = False
            flag_attr = False
            flag_text = False

            if tag is None:
                flag_tag = True
            else:
                flag_tag = each_tag == tag
            if attr is None:
                flag_attr = True
            else:
                if set(attr.keys()).issubset(set(each_attr.keys())):
                    check_list = []
                    for k in attr.keys():
                        check_list.append(attr[k] == each_attr[k])
                    if False not in check_list:
                        flag_attr = True
            if text is None:
                flag_text = True
            else:
                if each_text == text:
                    flag_text = True

            if flag_tag and flag_attr and flag_text:
                node_list.append(each)

        return node_list

    @staticmethod
    def get_tag(node):
        """
        获取节点标签名
        :param node:
        :return:
        """
        return node.tag

    @staticmethod
    def get_attr(node):
        """
        获取节点属性值
        :param node:
        :return:
        """
        return node.attrib

    @staticmethod
    def set_attr(node, attr_dict):
        """
        设置节点属性值
        :param node:
        :param attr_dict:
        :return:
        """
        node.attrib = attr_dict

    @staticmethod
    def change_attr(node, attr_name, attr_value):
        """
        修改指定属性值
        :param node:
        :param attr_name:
        :param attr_value:
        :return:
        """
        if attr_name not in node.attrib.keys():
            return
        else:
            node.attrib[attr_name] = attr_value

    @staticmethod
    def add_attr(node, attr_name, attr_value):
        """
        添加属性值
        :param node:
        :param attr_name:
        :param attr_value:
        :return:
        """

        if attr_name in node.attrib.keys():
            return
        else:
            node.attrib[attr_name] = attr_value

    @staticmethod
    def del_attr(node, attr_name):
        if attr_name not in node.attrib.keys():
            return
        else:
            del node.attrib[attr_name]

    @staticmethod
    def get_text(node):
        """
        获取节点文本信息
        :param node:
        :return:
        """
        if isinstance(node.text, str):
            return node.text.strip()
        else:
            return ''

    @staticmethod
    def set_text(node, text):
        """
        设置节点文本
        :param node:
        :param text:
        :return:
        """
        node.text = text

    @staticmethod
    def create_root_node(tag, attr={}, text=''):
        """
        创建根节点
        :param tag: str: 根节点标签名
        :param attr: dict: 根节点属性字典
        :param text: str: 根节点文本信息
        :return:
        """
        root_node = ET.Element(tag, attr)
        root_node.text = text
        return root_node

    @staticmethod
    def append_node(p_node, tag='undefined', attr={}, text='', element=None):
        """
        添加子节点
        :param p_node: Element: 父节点
        :param tag: str: 添加节点标签名
        :param attr: dict: 添加节点属性值
        :param text: str: 添加节点文本信息
        :param element: TODO 本来想做一个直接添加查询出的元素，但是查询出的元素是包含子节点信息的 尝试clear
        :return:
        """
        if element is None:
            node = ET.Element(tag, attr)
            node.text = text
            p_node.append(node)
        else:
            if isinstance(element, ET.Element):
                p_node.append(element)

    @staticmethod
    def del_node(p_node, node):
        pass
        # p_node.remove(node)

    @staticmethod
    def write_xml(root_node, out_path, encoding="UTF-8", xml_declaration=True, pretty_xml=True):

        def indent(elem, level=0):
            """对xml文档进行格式化"""
            i = "\n" + level * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        if pretty_xml:
            indent(root_node, 0)
        tree = ET.ElementTree(root_node)
        tree.write(out_path, encoding=encoding, xml_declaration=xml_declaration)
