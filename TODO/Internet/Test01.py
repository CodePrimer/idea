import socket

if __name__ == '__main__':

    # 客户端
    # 先创建一个socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 建立连接
    s.connect(('blog.csdn.net', 80))
    # 发送数据
    # [请求首行] 请求方式 请求路径 协议和版本
    # [请求头信息] 请求头名称:请求头内容（key:value）
    # [空行] 用于和请求体隔开
    # [请求体] GET方法没有请求体，POST方法有请求体
    connect_data = 'POST /weixin_42924891/article/details/85868278 HTTP/1.1\r\n' \
                   'Host:blog.csdn.net\r\n' \
                   'Connection: keep-alive\r\n' \
                   '\r\n'
    s.send(bytes(connect_data, encoding='utf8'))    # 发送的数据必须是byte数据格式
    # 接收数据
    buffer = []
    while True:
        d = s.recv(1024)
        if d:
            buffer.append(str(d, encoding='utf-8'))
        else:
            break
    data = ''.join(buffer)

    header, html = data.split('\r\n\r\n', 1)
    print(header)
    with open(r'C:\Users\wangbin\Desktop\1\baidu.html', 'w', encoding="utf-8") as f:
        f.write(html)
    print('Finish')


