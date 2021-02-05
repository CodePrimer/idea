# -*- coding: utf-8 -*-

import numpy as np

"""
+           加
-           减
*           乘
/           除
**          次方
np.log()    e为底对数
np.log10()  10为底对数
np.log2()   2为底对数
np.exp()    e为底指数

np.sin()    正弦函数
np.cos()    余弦函数
np.tan()    正切函数

"""


if __name__ == '__main__':

    b1 = np.ones((2, 3))
    b2 = np.ones((2, 3))
    b2[0][0] = 2
    b2[0][1] = 3
    b2[0][2] = 4

    print(b1)
    print('\n')
    print(b2)
    print('\n')

    string = 'b1+b2*2/3'
    b3 = eval(string)
    print(b3)

    print('Finish')
