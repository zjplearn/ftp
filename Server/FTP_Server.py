"""
ftp 文件服务器
并发网络功能训练
"""

from socket import *
from threading import Thread
import sys, os
import time

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)
# 文件库路径
FTP = "/home/zjplinux/Documents/month02/net_concur/"


def handle(c):
    # print("Connection from:", c.getpeername())
    data = c.recv(1024).decode()
    FTP_PATH = FTP + data + '/'
    # print(FTP_PATH)
    ftp = FtpServer(c, FTP_PATH)
    while True:
        data = c.recv(1024).decode()
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.strip()[1:]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.strip()[1:]
            ftp.do_put(filename)


# 将客户端请求功能封装为类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.FTP_PATH = FTP_PATH

    def do_list(self):
        # 获取文件列表
        files = os.listdir(self.FTP_PATH)
        if not files:
            self.connfd.send("该文件类别为空".encode())
            return
        else:
            self.connfd.send(b'OK')
        time.sleep(0.1)
        # 保证不是隐藏文件，  文件类型是普通文件
        fls = ''
        for file in files:
            if file[0] != '.' and os.path.isfile(self.FTP_PATH + file):
                fls += file + '\n'

        self.connfd.send(fls.encode())

    def do_get(self, filename):
        try:
            # print(self.FTP_PATH + filename)
            fd = open(self.FTP_PATH + filename, 'rb')
        except FileNotFoundError:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
        # 发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self, filename):
        if filename in os.listdir(self.FTP_PATH):
            self.connfd.send("文件已存在".encode())
            return
        else:
            self.connfd.send(b'OK')
        fd = open(self.FTP_PATH + filename, 'wb')
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()


# 网络搭建
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)
    print("Listen to the Port:", PORT, '....', sep='')

    while True:
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("服务端退出")
        except Exception as e:
            print(e)
            continue
        print("连接的客户端:", addr)
        # 创建线程处理请求
        client = Thread(target=handle, args=(c,))
        client.setDaemon(True)
        client.start()


if __name__ == "__main__":
    main()
