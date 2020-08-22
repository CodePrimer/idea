# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/18 20:07

"""
    png图片中某个值设置为透明并输出
"""

import cv2
import numpy as np


if __name__ == '__main__':

    inputImg = r"C:\Users\Think\Desktop\taihu_fre.png"
    outputImg = r"C:\Users\Think\Desktop\taihu_fre_alpha.png"
    alphaRgb = (235, 235, 235)

    img = cv2.imread(inputImg)

    b_channel, g_channel, r_channel = cv2.split(img)

    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255

    # Alpha波段设置为0为全透明
    alpha_channel[np.logical_and(b_channel == alphaRgb[2], g_channel == alphaRgb[1], r_channel == alphaRgb[0])] = 0

    img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

    cv2.imwrite(outputImg, img_BGRA)

