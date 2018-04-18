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
import json
import struct
import hashlib
from collections import OrderedDict
#from Crypto.Cipher import AES


FILEPATH = r'E:\service'    #windows文件存储
#FILEPATH = '/home/root/work/cloud_storage/server'    #LINUX文件存储路径
ADDR = ('0.0.0.0',7000)
TRANSMISSION_END_CODE = 'CLOUD_STORAGE_TRANSMISSION_END.'
JSONNAME = 'file_info_ser.json'
CHUNKSIZE = 1024*1024*30

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

def send_fhead(cli_socket,filename,filesize):
    '''发送文件头信息，包括文件名和文件大小'''
    fhead = struct.pack('128sd', filename.encode('utf-8'), filesize)
    cli_socket.send(fhead)

def new_user(conn,addr):
    print('Accept new connection from {0}'.format(addr))
    send_welcome(conn)      #发送欢迎消息
    parent_file_name, parent_file_size = client_needto_transfer_file(conn) #接受客户端的父文件头信息,父文件名，父文件大小，服务器开始准备获取文件块

    fileuniquevalue_and_number = OrderedDict()
    fileuniquevalue_and_number['Parent_file_info'] = (parent_file_name,parent_file_size)

    folder_path = prepare_recv_file(conn)


    #校验用户文件，并发送json文件给用户让用户核对
    prepare_check_file(folder_path,fileuniquevalue_and_number)
    confirm_file_correct(conn,folder_path)

    conn.close()
    print('END')
def confirm_file_correct(conn,folder_path):
    '''将服务器获取的json发给用户进行比对'''
    print('开始与客户端比对json文件')
    json_file_path = os.path.join(folder_path,JSONNAME)
    check_value = get_file_check_value(json_file_path)
    conn.send(check_value.encode('utf-8'))
    print('比对文件结束')

def prepare_check_file(folder_path,fileunique_and_number):
    '''准备校验根据文件夹路径校验里面所有符合的文件，并将校验值和文件名添加到字典fileunique_and_number'''
    all_file_name_list = os.listdir(folder_path)
    need_check_file_list = sorted( [file_name for file_name in all_file_name_list if file_name.isdigit()] )
    print('需要校验的文件列表', need_check_file_list)
    for check_file in need_check_file_list:
        check_file_path = os.path.join(folder_path, check_file)
        check_value = get_file_check_value(check_file_path) #根据文件绝对路径获取校验值
        fileunique_and_number[check_value] = int(check_file) #将键值对(校验值:文件名)加入到字典fileunique_and_number中
    print('所有文件校验结束,将结果字典存储到json文件中')
    storage_file_info(folder_path,fileunique_and_number)

# def check_func(filepath):
#     '''校验专用函数(sha256)'''
#     check = hashlib.sha256()
#     with open(filepath,'rb') as file:
#         data = file.read(CHUNKSIZE)
#         check.update(data)
#         check_value = check.hexdigest()
#     return check_value
def get_file_check_value(filepath):
    '''根据文件路径获取这个文件的校验值并返回'''
    check = hashlib.sha256()  # 使用sha256校验值作为文件唯一的身份表示
    with open(filepath, 'rb') as file:
        data = file.read(CHUNKSIZE) #从文件读取30M,因为文件最大为CHUNKSIZE,所以如果文件没问题，即读取文件所有内容
        check.update(data)
        check_value = check.hexdigest()
    return check_value

def storage_file_info(storage_file_path,fileuniquevalue_and_number):
    '''将生成的文件排序名及效验值的字典保存为json'''
    with open(os.path.join(storage_file_path,JSONNAME),'w') as fp_json:
        fp_json.write(json.dumps(fileuniquevalue_and_number))
    print('保存json成功')

def client_needto_transfer_file(conn):
    '''代码暂时和get_fileinfo函数相同'''
    parent_file_name, parent_file_size = get_fileinfo(conn)
    print('客户端发送需要传输文件的请求，文件名{0}，文件大小{1}'.format(parent_file_name,parent_file_size))
    return (parent_file_name,parent_file_size)

# def prepare_encrypt_file(folder_path):
#     all_file_name_list = os.listdir(folder_path)
#     need_encrypt_file = [file_name for file_name in all_file_name_list if file_name.isdigit()]
#     print('需要加密的文件列表',need_encrypt_file)
#     for encrypt_file in need_encrypt_file:
#         encrypt_file_path = os.path.join(folder_path,encrypt_file)  #获得需要加密的文件的绝对路径


def send_file(cli_socket,filepath):
    '''发送文件信息及文件内容专用函数'''
    if os.path.exists(filepath) and os.path.isfile(filepath):
        #fhead = struct.pack('128sd',os.path.basename(filepath).encode('utf-8'),os.path.getsize(filepath))
        send_fhead(cli_socket,JSONNAME,os.path.getsize(filepath))
        print('发送的文件名{0},文件大小{1}'.format(os.path.basename(filepath),os.path.getsize(filepath)))

        with open(filepath, 'rb') as fp:
            while True:
                data = fp.read(1024)
                if not data:
                    print('{0} 文件发送完毕...'.format(filepath))
                    break
                cli_socket.send(data)

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
    return folder_path

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