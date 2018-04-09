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
from Crypto.Cipher import AES

FILEPATH = '/home/root/trash'
ADDR = ('0.0.0.0',7000)

def cloud_service():
    ser_socket = socket_bind()
    while True:
        conn, addr = ser_socket.accept()
        new_thread = threading.Thread(target=new_user,args=(conn,addr))
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

def get_fileinfo(conn):
    fileinfo_size = struct.calcsize('128sd')
    buf = conn.recv(fileinfo_size)
    filename, filesize = struct.unpack('128sd',buf)     #windows与linux long的字节分配不同，故使用double
    filesize = int(filesize)
    filename = str(filename.strip(b'\x00'),encoding='utf-8')    #将文件名字节去除空字节，并转化为字符串
    return (filename,filesize)

def new_user(conn,addr):
    print('Accept new connection from {0}'.format(addr))
    send_welcome(conn)      #发送欢迎消息
    filename, filesize = get_fileinfo(conn)      #获取文件名称及大小信息
    new_filename = os.path.join(FILEPATH,filename)
    print(new_filename,filesize)
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