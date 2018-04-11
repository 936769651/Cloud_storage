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
#from Crypto.Cipher import AES

#FILEPATH = '/home/root/trash'
FILEPATH = r'E:\service'
ADDR = ('0.0.0.0',7000)
TRANSMISSION_END_CODE = 'CLOUD_STORAGE_TRANSMISSION_END.'

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
    '''获取待获取的文件信息(文件名字+文件大小)'''
    fileinfo_size = struct.calcsize('128sd')
    buf = conn.recv(fileinfo_size)
    filename, filesize = struct.unpack('128sd',buf)     #windows与linux long的字节分配不同，故使用double
    filesize = int(filesize)
    filename = str(filename.strip(b'\x00'),encoding='utf-8')    #将文件名字节去除空字节，并转化为字符串
    return (filename,filesize)

def new_user(conn,addr):
    print('Accept new connection from {0}'.format(addr))
    send_welcome(conn)      #发送欢迎消息

    prepare_recv_file(conn)
    conn.close()
    print('连接关闭')

def prepare_recv_file(conn):
    '''在获取文件文件前进行准备工作，如创建临时文件夹'''
    filename, filesize = get_fileinfo(conn)  # 一旦获取文件名称及大小信息，说明客户端要传输文件，下一步服务器创建临时文件夹
    print('用户准备传输文件')
    folder_path = make_folder()
    while True:
        recv_file(conn,folder_path,filename,filesize)
        print('一个文件获取完成')
        filename, filesize = get_fileinfo(conn)
        if(judge_trasmission_end(filename,filesize)):
            print('获得传输结束指令')
            break
    print('传输结束')

def judge_trasmission_end(filename,filesize):
    if filename == TRANSMISSION_END_CODE and filesize == 0:
        return True
    return False

def recv_file(conn,folder_path,filename,filesize):
    '''获取文件专用函数'''
    storage_file_path = os.path.join(folder_path, filename)
    print('当前文件保存路径是{0}'.format(storage_file_path))
    recvd_size = 0
    fp = open(storage_file_path, 'wb')
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

def make_folder():
    folder_name = str(time.time())
    folder_path = os.path.join(FILEPATH, folder_name)
    os.mkdir(folder_path)
    return folder_path

if __name__ == '__main__':
    cloud_service()