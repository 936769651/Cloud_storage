#!/usr/bin/python3
# _*_ coding=utf-8 _*_

'''
service.py
'''

import socket
import threading
import time
import sys
import os
import struct

FILEPATH = r'E:\service'
ADDR = ('127.0.0.1',7000)

def cloud_service():
    ser_socket = socket_bind()
    while True:
        conn, addr = ser_socket.accept()
        new_thread = threading.Thread(target=deal_data,args=(conn,addr))
        new_thread.start()

def socket_bind():
    try:
        ser_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        ser_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        ser_socket.bind(ADDR)    #绑定自身所有地址
    except socket.error as msg:
        print('socket_bind error: ' + msg)
        sys.exit(1)

    ser_socket.listen(3)
    print('Socket bind success,start listen')
    return ser_socket

def send_welcome(conn):
    welcome = 'Hi,welcome to cloud storage!'.encode('utf-8')
    conn.send(welcome)

def deal_data(conn,addr):
    print('Accept new connection from {0}'.format(addr))
    send_welcome(conn)
    fileinfo_size = struct.calcsize('128sl')
    buf = conn.recv(fileinfo_size)

    if buf:

        filename, filesize = struct.unpack('128sl',buf)
        filename = str(filename.strip(b'\x00'),encoding='utf-8')    #将文件名字节去除空字节，并转化为字符串
        new_filename = os.path.join(FILEPATH,filename)
        print(new_filename)
        recvd_size = 0
        fp = open(new_filename,'wb')
        print('Start receiving...')

        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                data = conn.recv(1024)
                recvd_size += len(data)
            else:
                data = conn.recv(filesize - recvd_size)
                recvd_size = filesize
            fp.write(data)
        fp.close()
        print('End receive...')
    conn.close()


if __name__ == '__main__':
    cloud_service()