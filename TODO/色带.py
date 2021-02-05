# -*- coding: utf-8 -*-
# @Author : wangbin
# @Time : 2020/8/18 20:07

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def RGB_to_Hex(rgb):
    RGB = rgb.split(',')  # 将RGB格式划分开来
    color = '#'
    for i in RGB:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    print(color)
    return color


def RGB_list_to_Hex(RGB):
    # RGB = rgb.split(',')  # 将RGB格式划分开来
    color = '#'
    for i in RGB:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    print(color)
    return color


def Hex_to_RGB(hex):
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    rgb = str(r) + ',' + str(g) + ',' + str(b)
    print(rgb)
    return rgb, [r, g, b]


def gradient_color(color_list, color_sum=1000):
    color_center_count = len(color_list)

    color_sub_count = int(color_sum / (color_center_count - 1))
    color_index_start = 0
    color_map = []
    for color_index_end in range(1, color_center_count):
        color_rgb_start = color_list[color_index_start]
        color_rgb_end = color_list[color_index_end]
        # color_rgb_start = Hex_to_RGB(color_list[color_index_start])[1]
        # color_rgb_end = Hex_to_RGB(color_list[color_index_end])[1]
        r_step = (color_rgb_end[0] - color_rgb_start[0]) / color_sub_count
        g_step = (color_rgb_end[1] - color_rgb_start[1]) / color_sub_count
        b_step = (color_rgb_end[2] - color_rgb_start[2]) / color_sub_count

        now_color = color_rgb_start
        color_map.append(RGB_list_to_Hex(now_color))
        for color_index in range(1, color_sub_count):
            now_color = [now_color[0] + r_step, now_color[1] + g_step, now_color[2] + b_step]
            color_map.append(RGB_list_to_Hex(now_color))
            color_index_start = color_index_end
    return color_map


if __name__ == '__main__':
    input_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_map_list = gradient_color(input_colors)

    start_y = 0
    rect_height = 0.001
    fig, ax = plt.subplots(1)
    for each in color_map_list:
        rect = patches.Rectangle((0, start_y), 0.2, rect_height, facecolor=each)
        start_y += rect_height
        ax.add_patch(rect)
    plt.show()
    print('Finish')
