# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/18 20:07

"""
    png图片中某个值设置为透明并输出
"""

import cv2
import numpy as np


if __name__ == '__main__':

    inputImg = r"E:\FrontLearning\CSS\icon.png"
    outputImg = r"E:\FrontLearning\CSS\icon1.png"

    alphaRgb = [(255, 255, 255)]
    img = cv2.imread(inputImg)

    b_channel, g_channel, r_channel = cv2.split(img)

    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255

    # # 透明有效区域
    # activateRegionLoc = np.zeros(b_channel.shape, dtype=b_channel.dtype)
    # activateRegionLoc[63:1904, 52:2056] = 1
    #
    # # 图例范围
    # activateRegionLoc[1718:1873, 84:420] = 0

    # Alpha波段设置为0为全透明
    for each in alphaRgb:
        colorAlphaLoc = np.logical_and(b_channel == each[2], g_channel == each[1], r_channel == each[0])
        # loc = np.logical_and(activateRegionLoc == 1, colorAlphaLoc)
        alpha_channel[colorAlphaLoc] = 0

    # # 修正特殊颜色
    # specialLoc = np.logical_and(b_channel == 0, g_channel == 255, r_channel == 0)
    # specialLoc[1591:1873, 84:420] = False
    # b_channel[specialLoc] = 255
    # g_channel[specialLoc] = 255
    # r_channel[specialLoc] = 255

    img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

    cv2.imwrite(outputImg, img_BGRA)

    print('Finish')