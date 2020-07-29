from GeoTiffFile import GeoTiffFile
import cv2
import numpy as np
from PIL import Image


def calculate_value(tif_array):
    array = tif_array[tif_r != -9999].flatten()  # 去除-9999无效值
    # array_min = np.min(array)
    # array_max = np.max(array)
    array_min = np.percentile(array, 2)
    array_max = np.percentile(array, 98)
    print(array_min)
    print(array_max)
    stretch_min = 0
    stretch_max = 255


    # 转换公式：y = (x - array_min)/(array_max - array_min) * (stretch_max - stretch_min) + stretch_min
    stretch_array = (tif_array - array_min) / (array_max - array_min) * (stretch_max - stretch_min) + stretch_min
    stretch_array = stretch_array.astype(np.int)
    stretch_array[stretch_array < 0] = 0
    stretch_array[stretch_array > 255] = 255
    return stretch_array


if __name__ == '__main__':

    tif_path = r'E:\zktq\AQUA_MODIS_250_L2_20200305133000_061_00.tif'
    # tif_path = r'E:\zktq\AQUA_MODIS_L2_202006191228_250_00_00.tif'

    tif_obj = GeoTiffFile(tif_path)
    tif_obj.readTif()
    width = tif_obj.getWidth()
    height = tif_obj.getHeight()
    tif_r = tif_obj.getBandData(0).astype(np.float)
    tif_g = tif_obj.getBandData(1).astype(np.float)
    tif_b = tif_obj.getBandData(0).astype(np.float)
    stretch_r = calculate_value(tif_r)
    stretch_g = calculate_value(tif_g)
    stretch_b = calculate_value(tif_b)
    rgb_array = np.zeros((height, width, 3))
    rgb_array[:, :, 0] = stretch_r
    rgb_array[:, :, 1] = stretch_g
    rgb_array[:, :, 2] = stretch_b
    rgb_image = Image.fromarray(rgb_array, mode='RGB')
    rgb_image.show()
    print('Finish')




