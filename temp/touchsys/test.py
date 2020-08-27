# -*- coding: utf-8 -*-

import sys

"""
This module provides access to some objects used or maintained by the
interpreter and to functions that interact strongly with the interpreter.

# 该模块提供对解释器使用或维护的某些对象的访问，以及对与解释器强交互的函数的访问。

Dynamic objects:    # 动态对象

argv -- command line arguments; argv[0] is the script pathname if known
path -- module search path; path[0] is the script directory, else ''
modules -- dictionary of loaded modules

# argv—命令行参数；argv[0]是脚本路径名（如果已知）
# path--模块搜索路径；路径[0]是脚本目录，否则为''
# modules--加载模块字典

displayhook -- called to show results in an interactive session
excepthook -- called to handle any uncaught exception other than SystemExit
  To customize printing in an interactive session or to install a custom
  top-level exception handler, assign other functions to replace these.



exitfunc -- if sys.exitfunc exists, this routine is called when Python exits
  Assigning to sys.exitfunc is deprecated; use the atexit module instead.

stdin -- standard input file object; used by raw_input() and input()
stdout -- standard output file object; used by the print statement
stderr -- standard error object; used for error messages
  By assigning other file objects (or objects that behave like files)
  to these, it is possible to redirect all of the interpreter's I/O.

last_type -- type of last uncaught exception
last_value -- value of last uncaught exception
last_traceback -- traceback of last uncaught exception
  These three are only available in an interactive session after a
  traceback has been printed.

exc_type -- type of exception currently being handled
exc_value -- value of exception currently being handled
exc_traceback -- traceback of exception currently being handled
  The function exc_info() should be used instead of these three,
  because it is thread-safe.

Static objects:

float_info -- a dict with information about the float inplementation.
long_info -- a struct sequence with information about the long implementation.
maxint -- the largest supported integer (the smallest is -maxint-1)
maxsize -- the largest supported length of containers.
maxunicode -- the largest supported character
builtin_module_names -- tuple of module names built into this interpreter
version -- the version of this interpreter as a string
version_info -- version information as a named tuple
hexversion -- version information encoded as a single integer
copyright -- copyright notice pertaining to this interpreter
platform -- platform identifier
executable -- absolute path of the executable binary of the Python interpreter
prefix -- prefix used to find the Python library
exec_prefix -- prefix used to find the machine-specific Python library
float_repr_style -- string indicating the style of repr() output for floats
dllhandle -- [Windows only] integer handle of the Python DLL
winver -- [Windows only] version number of the Python DLL
__stdin__ -- the original stdin; don't touch!
__stdout__ -- the original stdout; don't touch!
__stderr__ -- the original stderr; don't touch!
__displayhook__ -- the original displayhook; don't touch!
__excepthook__ -- the original excepthook; don't touch!

Functions:

displayhook() -- print an object to the screen, and save it in __builtin__._
excepthook() -- print an exception and its traceback to sys.stderr
exc_info() -- return thread-safe information about the current exception
exc_clear() -- clear the exception state for the current thread
exit() -- exit the interpreter by raising SystemExit
getdlopenflags() -- returns flags to be used for dlopen() calls
getprofile() -- get the global profiling function
getrefcount() -- return the reference count for an object (plus one :-)
getrecursionlimit() -- return the max recursion depth for the interpreter
getsizeof() -- return the size of an object in bytes
gettrace() -- get the global debug tracing function
setcheckinterval() -- control how often the interpreter checks for events
setdlopenflags() -- set the flags to be used for dlopen() calls
setprofile() -- set the global profiling function
setrecursionlimit() -- set the max recursion depth for the interpreter
settrace() -- set the global debug tracing function
"""


def test_sysargv():
    """sys.argv功能测试函数
    
    sys.argv 是获取运行python文件的时候命令行参数，且以list形式存储参数
    sys.argv[0] 获取当前module的名字
    """

    cmd_args = sys.argv

    if len(cmd_args) == 1:
        print("Current Module Name is : %s" % cmd_args[0])
    else:
        i = 0
        for arg in cmd_args:
            if i == 0:
                print("Current Module Name is : %s" % cmd_args[0])
                i += 1
            else:
                print("args Number%d is : %s" % (i, cmd_args[i]))
                i += 1


def test_syspath():
    """sys.path功能测试函数
    sys.path是python的搜索模块的路径集，是一个list

    """
    print sys.path

    # sys.path.append(path)添加指定搜索路径
    sys.path.append("D:/PATH")
    print sys.path


def test_sysmodules():

    module_dict = sys.modules
    if "os" in module_dict.keys():
        print("os module be import. ")



if __name__ == "__main__":

    # cmd参数输入
    test_sysargv()

    # 编译器模块搜索路径
    test_syspath()

    sys.modules


    print("====== process finished ======")