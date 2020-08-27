# -*- coding: utf-8 -*-
import numpy as np

# numpy数据类型
# Numpy类型	        C型	            描述
# np.int8	        int8_t	        字节（-128到127）
# np.int16	        int16_t	        整数（-32768至32767）
# np.int32	        int32_t	        整数（-2147483648至2147483647）
# np.int64	        int64_t	        整数（-9223372036854775808至9223372036854775807）
# np.uint8	        uint8_t	        无符号整数（0到255）
# np.uint16	        uint16_t	    无符号整数（0到65535）
# np.uint32	        uint32_t	    无符号整数（0到4294967295）
# np.uint64	        uint64_t	    无符号整数（0到18446744073709551615）
# np.intp	        intptr_t	    用于索引的整数，通常与索引相同 ssize_t
# np.uintp	        uintptr_t	    整数大到足以容纳指针
# np.float32	    float
# np.float64 	    double	        请注意，这与内置python float的精度相匹配。
# np.complex64	    float complex	复数，由两个32位浮点数（实数和虚数组件）表示
# np.complex128 	double complex	请注意，这与内置python 复合体的精度相匹配

if __name__ == "__main__":

    # 创建numpy类型的变量
    a = np.int8(1.0)        # 单个变量
    print(np.dtype(a))

    arr = np.array([3.5, 2.5, 1.5])    # 数组
    print(arr)

    # numpy类型转换
    a = np.float16(a)       # 单个变量支持用np类型转换函数
    print(np.dtype(a))

    arr = arr.astype(np.int8)    # 某些版本需要使用变量接收，无法直接修改属性
    print(arr)
    print(arr.dtype)

    print("---------------END---------------")