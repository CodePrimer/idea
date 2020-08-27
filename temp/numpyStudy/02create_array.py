# -*- coding: utf-8 -*-
import numpy as np

# 创建数组有5种常规机制：
#
# 1.从其他Python结构转换（例如，列表，元组）
# 2.内在的numpy数组创建对象（例如，arange，one，zeros等）
# 3.从标准或自定义格式读取磁盘阵列
# 4.通过使用字符串或缓冲区从原始字节创建数组
# 5.使用特殊库函数（例如，随机）


if __name__ == "__main__":

    """1.从其他python结构转换"""
    x = np.array([2, 3, 1, 0])      # 创建整型numpy数组
    print(x)
    print(x.dtype)                  # int32

    x = np.array([2, 3, 1.0, 0])    # 创建浮点型numpy数组
    print(x)
    print(x.dtype)                  # float64

    x = np.array([[1. + 0.j, 2. + 0.j], [0. + 0.j, 0. + 0.j], [1. + 1.j, 3. + 0.j]])
    print(x)
    print(x.dtype)

    """2.内在的numpy数组创建对象"""
    # np.zeros()创建0值数组，默认类型为是float64。
    arr1 = np.zeros((2, 3))     # (2, 3) 先行后列
    print(arr1)
    arr1 = np.zeros((2, 3), dtype=np.int8)
    print(arr1)

    # np.ones()创建1值数组，默认类型为是float64。
    arr2 = np.ones((3, 4))
    print(arr2)

    # np.arange()将创建具有定期递增值的数组
    arr3 = np.arange(10)        # 创建0-9的索引数组
    print(arr3)
    arr3 = np.arange(2, 10, dtype=float)    # 创建
    arr3 = np.arange(2, 3, 0.1)
    print(arr3)

