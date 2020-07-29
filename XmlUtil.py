# !/usr/bin/python3
# -*- coding: utf-8  -*-
# -*- author: htht -*-

import xml.dom.minidom
from xml.dom.minidom import Document


class XmlUtil(object):

    """
    XML文件通用方法类，实现以下功能：
    1.写入XML文件信息
    2.读取XML文件信息 TODO
    """

    """
    1. nodeType的意思，不同的数字代表不同的值，其中前三个为，1：Element， 2：Attribute， 3：Text
    """

    def __init__(self):
        pass

    @staticmethod
    def get_root_node(file_path):
        """获取xml根节点"""
        dom_tree = xml.dom.minidom.parse(file_path)
        root_node = dom_tree.documentElement  # 获取根节点
        return root_node

    @staticmethod
    def get_node_attr(node):
        """
        获取节点属性信息
        :param node: xml节点
        :return: dict {属性名1:属性值1,属性名2:属性值2}
        """
        attrInfo = {}
        if not node.hasAttributes():
            return attrInfo
        for i in range(node.attributes.length):
            attrInfo[node.attributes.item(i).name] = node.attributes.item(i).value
        return attrInfo

    @staticmethod
    def get_node_text(node):
        pass

    @staticmethod
    def createDom():
        """创建文档结构树"""
        dom = Document()
        return dom

    @staticmethod
    def createRootNode(dom, rootName, attrInfo=None, text=None):
        """
        添加根节点
        :param dom: 文档对象
        :param rootName: 根节点名
        :param attrInfo: 根节点属性信息
        :param text: 根节点文本信息
        :return:
        """
        if not isinstance(rootName, str):
            return
        rootNode = dom.createElement(rootName)
        if attrInfo and isinstance(attrInfo, dict):
            XmlUtil.addAttr(rootNode, attrInfo)
        if text and isinstance(text, str):
            XmlUtil.addText(dom, rootNode, text)
        dom.appendChild(rootNode)
        return rootNode

    @staticmethod
    def appendNode(dom, pNode, nodeName, attrInfo=None, text=None):
        """
        添加子节点
        :param dom: 文档对象
        :param pNode: 父节点
        :param nodeName: 添加节点名
        :param attrInfo: 添加节点属性信息
        :param text: 添加节点文本信息
        :return:
        """
        if not isinstance(nodeName, str):
            return
        node = dom.createElement(nodeName)
        if attrInfo and isinstance(attrInfo, dict):
            XmlUtil.addAttr(node, attrInfo)
        if text and isinstance(text, str):
            XmlUtil.addText(dom, node, text)
        pNode.appendChild(node)
        return node

    @staticmethod
    def addAttr(node, attrInfo):
        """
        添加节点属性信息
        :param node: 被添加节点对象
        :param attrInfo: 属性信息字典 {"属性名1":属性值1,...}
        :return:
        """
        if not isinstance(attrInfo, dict):
            return
        for key in attrInfo.keys():
            node.setAttribute(key, attrInfo[key])

    @staticmethod
    def addText(dom, node, text):
        """
        添加节点文本信息
        :param dom: 文档对象
        :param node: 被添加节点对象
        :param text: 添加文本信息
        :return:
        """
        if not isinstance(text, str):
            return
        textNode = dom.createTextNode(text)
        node.appendChild(textNode)

    @staticmethod
    def saveDom(dom, savePath):
        """
        存储xml文件
        :param dom: 文档对象
        :param savePath: 存储路径
        :return:
        """
        with open(savePath, 'w', encoding='utf-8') as f:
            dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')


if __name__ == "__main__":

    domTest = XmlUtil.createDom()
    XmlUtil.createRootNode()

