# -- coding: utf-8 --

import piesdk_pymod


class Layer(object):
    """图层类"""

    # 图层类型常量
    SHAPE_POINT = 1           # 点矢量
    SHAPE_POLYLINE = 2        # 线矢量
    SHAPE_POLYGON = 3         # 面矢量
    TIFF_SINGLE_BAND = 4      # 单波段栅格
    TIFF_MUL_BAND = 5         # 多波段栅格

    def __init__(self, layer_name, layer_type, layer_source, layer_rander):
        self.name = layer_name        # str: 图层名
        self.type = layer_type        # int: 图层类型
        self.source = layer_source    # str: 图层数据源路径
        self.rander = layer_rander    # str: 图层渲染文件路径


class Mapping(object):

    def __init__(self, file_path):
        self.__pmd_path = file_path       # 模板文件路径
        self.__tempdir = ""               # 临时文件夹路径
        self.__layers = []                # 图层列表
        self.__replace_text = {}          # 替换文本字典
        self.__extent = []                # 数据框范围[xmin, xmax, ymin, ymax]
        self.__extent_percentage = None   # 缩放百分比

    def add_layer(self, layer_obj):
        self.__layers.append(layer_obj)

    def set_tempdir(self, dir_path):
        self.__tempdir = dir_path

    def set_replace_text(self, info):
        self.__replace_text = info

    def set_extent(self, xmin, xmax, ymin, ymax):
        self.__extent = [xmin, xmax, ymin, ymax]

    def set_extent_percentage(self, percentage):
        self.__extent_percentage = percentage

    def export_pic(self, out_path, dpi):
        map_doc = piesdk_pymod.MapDocument()
        map_doc.LoadFile(self.__pmd_path)

        for i in range(len(self.__layers)):
            lyr_obj = piesdk_pymod.Layer()
            source_path = self.__layers[i].source
            lyr_obj.LoadFile(source_path)
            source_type = self.__layers[i].type
            if source_type in [Layer.SHAPE_POINT, Layer.SHAPE_POLYLINE, Layer.SHAPE_POLYGON]:
                piesdk_pymod.VectorRenderByClassify(self.__layers[i].rander, lyr_obj)
                map_doc.AddLayer(lyr_obj, i, 0)
            elif source_type == Layer.TIFF_SINGLE_BAND:
                piesdk_pymod.RasterRenderByClassify(self.__layers[i].rander, lyr_obj)
                map_doc.AddLayer(lyr_obj, i, 0)
            else:
                piesdk_pymod.MultibandRasterRender(self.__layers[i].rander, lyr_obj)
                map_doc.AddLayer(lyr_obj, i, 0)

        # 替换文本
        Mapping.replace_text_ele(map_doc, self.__replace_text)

        if self.__extent:
            if self.__extent_percentage:
                scale = self.__extent_percentage
                ori_xmin = self.__extent[0]
                ori_xmax = self.__extent[1]
                ori_ymin = self.__extent[2]
                ori_ymax = self.__extent[3]
                xmin = (ori_xmax + ori_xmin) / 2 - ((ori_xmax - ori_xmin) * scale) / (100 * 2)
                xmax = (ori_xmax + ori_xmin) / 2 + ((ori_xmax - ori_xmin) * scale) / (100 * 2)
                ymin = (ori_ymax + ori_ymin) / 2 - ((ori_ymax - ori_ymin) * scale) / (100 * 2)
                ymax = (ori_ymax + ori_ymin) / 2 + ((ori_ymax - ori_ymin) * scale) / (100 * 2)
                map_doc.ChangeEnvelope(xmin, xmax, ymin, ymax, 0)
            else:
                map_doc.ChangeEnvelope(self.__extent[0], self.__extent[1], self.__extent[2], self.__extent[3], 0)

        # 输出图片
        piesdk_pymod.PageLayoutToImage(map_doc.GetPageLayout(), out_path, dpi)
        del map_doc

    @staticmethod
    def replace_text_ele(map_doc, replace_text_info):
        """
        文本元素替换
        :param map_doc: 文档对象
        :param replace_text_info: 替换字典{"文本对象名": {"替换前文本": "替换后文本"}}
        :return:
        """
        ele_list = map_doc.GetAllElement()
        for eleObj in ele_list:
            if eleObj.GetElementType() != 9:
                continue
            if not eleObj.GetName() in replace_text_info.keys():
                continue
            ele_name = eleObj.GetName()
            ele_text = eleObj.GetText()
            for key in replace_text_info[ele_name].keys():
                ele_text = ele_text.replace("{" + key + "}", replace_text_info[ele_name][key])
                eleObj.SetText(ele_text)


if __name__ == "__main__":

    # =====================================单个区域出图代码示例=================================================== #

    # pmd模板路径
    pmd_path = r"C:\Users\wangbin\Desktop\piemapping\SnowDepth.pmd"
    # 临时文件目录 TODO 用于存储裁切后的数据
    temp_dir = r"C:\Users\wangbin\Desktop\piemapping\tempdir"

    # TODO 这些数据源必须是以当前出图行政区划裁切过后的
    # 省界图层/渲染
    province_path = r"C:\Users\wangbin\Desktop\piemapping\data\AreaProvince.shp"
    province_rander = r"C:\Users\wangbin\Desktop\piemapping\rander\AreaProvince_Rander.xml"
    # 产品文件路径/渲染路径
    tif_path = r"C:\Users\wangbin\Desktop\piemapping\data\SNW_DEPT_RCUR_202001111226_COOD_TERRA_MODIS_QHS.tif"
    tif_rander = r"C:\Users\wangbin\Desktop\piemapping\rander\SnowDepth.xml"
    # 市界图层/渲染
    city_path = r"C:\Users\wangbin\Desktop\piemapping\data\AreaCity.shp"
    city_rander = r"C:\Users\wangbin\Desktop\piemapping\rander\AreaCity_Rander.xml"
    # 县界图层/渲染
    county_path = r"C:\Users\wangbin\Desktop\piemapping\data\AreaCounty.shp"
    county_rander = r"C:\Users\wangbin\Desktop\piemapping\rander\AreaCounty_Rander.xml"
    # 背景图层/渲染
    background_path = r"C:\Users\wangbin\Desktop\piemapping\data\EOST_MODIS_QH_PRJ_L1_20200111_1226_0500M_clip.tif"
    background_rander = r"C:\Users\wangbin\Desktop\piemapping\rander\RGB.xml"

    # 创建mapping对象
    mapping_obj = Mapping(pmd_path)
    # 设置临时文件夹路径
    mapping_obj.set_tempdir(temp_dir)

    # 创建各图层对象
    tif_layer = Layer("tif", Layer.TIFF_SINGLE_BAND, tif_path, tif_rander)
    province_layer = Layer("province", Layer.SHAPE_POLYGON, province_path, province_rander)
    city_layer = Layer("city", Layer.SHAPE_POLYGON, city_path, city_rander)
    county_layer = Layer("county", Layer.SHAPE_POLYGON, county_path, county_rander)
    background_layer = Layer("rgb", Layer.TIFF_MUL_BAND, background_path, background_rander)

    # 添加图层信息
    # add_layer会将图层往一个列表中添加，所以要注意添加顺序
    # 最先添加的会在最底层，最后添加的会在最上层
    mapping_obj.add_layer(background_layer)
    mapping_obj.add_layer(tif_layer)
    mapping_obj.add_layer(province_layer)
    mapping_obj.add_layer(city_layer)
    mapping_obj.add_layer(county_layer)

    # 添加替换文本信息
    replace_text = {"title": {"yyyy": "2020", "MM": "04", "dd": "21", "HH": "18", "mm": "07", "regionName": "青海省"},
                    "date": {"yyyy": "2020", "MM": "04", "dd": "21"},
                    "info": {"SAT": "FY3B", "SEN": "VIRR", "RES": "500"}}
    mapping_obj.set_replace_text(replace_text)

    # [可选]设置数据框范围
    # 若不设置则以模板设置数据框范围为准
    # TODO 这里要先获取到当前的数据框经纬度范围
    mapping_obj.set_extent(89.401, 103.07, 31.6007, 39.2126)

    # [可选]设置数据框缩放百分比，数值越大数据矿范围越大
    mapping_obj.set_extent_percentage(105)

    # 专题图输出路径
    out_pic_path = r"C:\Users\wangbin\Desktop\piemapping\outpic\output_pic1.png"
    mapping_obj.export_pic(out_pic_path, 300)

