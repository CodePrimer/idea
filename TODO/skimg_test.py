
from skimage import measure, draw, io
import numpy as np
from PIL import Image

if __name__ == '__main__':
    # test_arr = np.rint(np.random.random((100, 100)))
    # labels = measure.label(test_arr, connectivity=1)

    img = np.zeros([100, 100])
    img[20:40, 60:80] = 250  # 矩形
    rr, cc = draw.circle(60, 60, 10)  # 小圆
    rr1, cc1 = draw.circle(20, 30, 15)  # 大圆
    img[rr, cc] = 180
    img[rr1, cc1] = 180
    a = Image.fromarray(img)
    # a.show()
    # 检测所有图形的轮廓
    contours = measure.find_contours(img, 0.5)
    for i in range(len(contours)):
        for j in range(len(contours[i])):
            print(contours[i][j])
            x_index = int(contours[i][j][1])
            y_index = int(contours[i][j][0])

    io.imsave(r'C:\Users\Think\Desktop\output\image.jpg', img.astype(np.uint8), dpi=300)
    print('finish')