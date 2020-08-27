# -- coding: utf-8 -- 

from lxml import etree

'''etree基础操作'''

def deep_search_nodes(root_node, pool):
    
    for each in root_node:
        if len(list(each)) != 0:
            deep_search_nodes(each, pool)
        pool.append(each)
    return pool

if __name__ == '__main__':
    
    print("-----START MAIN FUNCTION------")
    
    
#     # 创建根节点
#     root = etree.Element("root")
#     print(root.tag)         #打印节点名称
#     # 向根节点添加子节点方法1:直接创建节点并添加
#     root.append( etree.Element("child1") )
#     # 向根节点添加子节点方法2:使用subElement函数，第一个参数为父节点，第二个参数为子节点名称
#     child2 = etree.SubElement(root, "child2")
#     child3 = etree.SubElement(root, "child3")
#     print(etree.tostring(root))        #查看所有节点
#     
#     
#     # 对根节点操作近似数组操作
#     child = root[0]      # 按下标取节点
#     print(child.tag)
#     print(len(root))
#     # 遍历节点
#     children = list(root)
#     for child in root:      
#         print(child.tag)
#     
#     # 按下标插入子节点
#     root.insert(0, etree.Element("child0"))     
#     start = root[:1]
#     end = root[-1:]
#     print(start[0].tag)
#     print(end[0].tag)
#     
#     
#     # (根)节点测试
#     print(etree.iselement(root)) # test if it’s some kind of Element
#     if len(root): # test if it has
#         print("The root element has children")
#     
#     
#     # 属性值设置
#     root2 = etree.Element("root", interesting="totally")        # 初始化时直接添加属性值
#     print(root2.get("interesting"))     # 获取属性值
#     print(root.get("hello"))            # 若无该属性值返回None
#     root2.set("hello", "Huhu")          # 通过set接口添加属性值
#     print(root2.get("hello"))
#     
#     sorted(root2.keys())    # 直接以字典keys()方式获取属性列表
#     for attr_name, attr_value in root2.items():
#         print('%s = %r' %(attr_name, attr_value))
#         
#     attr_map = root2.attrib     # 节点.attrib获取属性值字典
#     print(attr_map)
#     attr_map["name"] = "wangbin"    # 这个直接操作了字典，就可以修改ROOT2节点内容，还是很强大的
#     print(root2.get("name"))        # 但是使用时需注意，容易修改原始值
#     
#     d = dict(root2.attrib)           # 若要获取属性值字典并进一步操作，需用dict函数转换
#     sorted(d.items())
#     
# 
#     # 文本设置
#     root3 = etree.Element("root")
#     root3.text = "TEXT"
#     print(root3.text)
#     etree.tostring(root)
#     
#     
#     # =========================================
#     # Tree iteration
#     root = etree.Element("root")
#     etree.SubElement(root, "child").text = "Child 1"
#     etree.SubElement(root, "child").text = "Child 2"
#     etree.SubElement(root, "another").text = "Child 3"
#     print(etree.tostring(root))
#     
#     for element in root.iter():
#         print("%s - %s" % (element.tag, element.text))
#     
#     # 如果你知道你只对一个标签感兴趣，
#     # 你可以将它的名字传递给iter()让它为你过滤。
#     # 从LXML 3.0开始 你也可以在迭代过程中传递多个标签来拦截多个标签。
#     for element in root.iter("child"):
#         print("%s - %s" % (element.tag, element.text))
    
    
    # 解析xml
    if __name__ == '__main__':
        sample_xml = r'C:\Users\wangbin\Desktop\xmlUtil\data\HJ1B-CCD1-11-72-20180819-L20003471167.XML'
        tree = etree.parse(sample_xml)
        root = tree.getroot()

        result = deep_search_nodes(root, [])

        print('-'*100)

        print(result)



        print("-----END MAIN FUNCTION------")