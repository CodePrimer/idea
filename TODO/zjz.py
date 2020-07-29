from PIL import Image
import numpy as np

if __name__ == '__main__':
    jpg_path = r'C:\Users\Think\Desktop\17026e7c6ff5a7564833170785b01a1.jpg'
    img = Image.open(jpg_path)
    print(img.format)
    print(img.size)  # 注意，省略了通道 (w，h)
    print(img.mode)  # L为灰度图，RGB为真彩色,RGBA为加了透明通道
    # img.show()  # 显示图片
    r, g, b = img.split()
    r_arr = np.array(r)
    g_arr = np.array(g)
    b_arr = np.array(b)
    w = np.logical_and(r_arr > 170, g_arr > 170, b_arr > 170)
    r_arr[w] = 255
    g_arr[w] = 255
    b_arr[w] = 255
    o_img = Image.merge("RGB", (Image.fromarray(r_arr), Image.fromarray(g_arr), Image.fromarray(b_arr)))
    o_img.save(r'C:\Users\Think\Desktop\11.jpg')

    print('finish')