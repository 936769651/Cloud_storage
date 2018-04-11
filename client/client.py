# _*_ coding=utf-8 _*_

'''
client.py
'''

import socket
import os
import sys
import struct
import time
import hashlib
import json

#ADDR = ('192.168.1.103',7000)
ADDR = ('127.0.0.1',7000)
FILEPATH = r'E:\client\mv.rmvb'    #代处理文件路径
CHUNKSIZE = 1024*1024*30        #每块文件30M
JSONNAME = '.file_info.json'
TRANSMISSION_END_CODE = 'CLOUD_STORAGE_TRANSMISSION_END.'

def cloud_client():
    '''主程序'''
    cli_socket = socket_bind()
    recv_welcome(cli_socket)
    folder_name = deal_file(FILEPATH)   #处理文件，并返回处理完文件的文件夹名，以时间戳命名
    folder_path = os.path.join(os.path.split(FILEPATH)[0],folder_name)  #获取存储分割文件的绝对路径
    send_file_in_folder(cli_socket,folder_path)
    cli_socket.close()
# def cloud_client():
#     cli_socket = socket_bind()
#     recv_welcome(cli_socket)
#     if os.path.isfile(FILEPATH):
#         fileinfo_size = struct.calcsize('128sd')
#         fhead = struct.pack('128sd',os.path.basename(FILEPATH).encode('utf-8'),os.stat(FILEPATH).st_size)
#         cli_socket.send(fhead)
#
#         fp = open(FILEPATH,'rb')
#         while True:
#             data = fp.read(1024)
#             if not data:
#                 print('{0} file send over...'.format(FILEPATH))
#                 break
#             cli_socket.send(data)
#         cli_socket.close()

def send_file_in_folder(cli_socket,folder_path):
    '''发送指定文件夹里被被分割完的文件，文件名必须是数字，否则不发送'''
    all_file_name_list = os.listdir(folder_path)
    split_file_name_list = list()    #获取所有以数字命名的文件
    for file_name in all_file_name_list:
        if file_name.isdigit():
            split_file_name_list.append(file_name)
    for file_name in split_file_name_list:
        send_file_path = os.path.join(folder_path,file_name)    #获取要发送的文件的绝对路径
        send_file(cli_socket,send_file_path)         #发送文件专用函数
    send_trasmission_end_code(cli_socket)

def send_trasmission_end_code(cli_socket):
    fhead = struct.pack('128sd', TRANSMISSION_END_CODE.encode('utf-8'), 0)
    cli_socket.send(fhead)
    print('发送传输结束指令')

def send_file(cli_socket,filepath):
    '''发送文件信息及文件内容专用函数'''
    if os.path.exists(filepath) and os.path.isfile(filepath):
        fhead = struct.pack('128sd',os.path.basename(filepath).encode('utf-8'),os.path.getsize(filepath))
        print('发送的文件名{0},文件大小{1}'.format(os.path.basename(filepath),os.path.getsize(filepath)))
        cli_socket.send(fhead)

        fp = open(filepath,'rb')
        while True:
            data = fp.read(1024)
            if not data:
                print('{0} 文件发送完毕...'.format(filepath))
                break
            cli_socket.send(data)

def deal_file(filepath):
    '''开始处理文件，最后返回分割文件保存路径'''
    if not os.path.exists(filepath) or not os.path.isfile(filepath):    #如果该路径不存在或不是文件，则退出
        print('{0} 该文件不符合条件，请检查'.format(filepath))
        return
    parent_path = os.path.split(filepath)[0]
    folder_name = '.' + str(int(time.time()))   #以时间戳作为临时文件夹名字
    storage_split_file_path = os.path.join(parent_path,folder_name)
    os.mkdir(storage_split_file_path)
    split_file(filepath,storage_split_file_path)
    return folder_name

def split_file(filepath,storage_split_file_path):
    '''分割文件，并生成小文件各自的效验值及数字排序'''
    fileuniquevalue_and_number = dict()
    filename = os.path.split(filepath)[1]
    parent_file_size = os.path.getsize(filepath)
    fileuniquevalue_and_number['Parent_file_info'] = (filename,parent_file_size)
    number = 0
    check = hashlib.sha256()        #使用sha256校验值作为文件唯一的身份表示
    with open(filepath,'rb') as parent_file:
        while True:
            data = parent_file.read(CHUNKSIZE)   #从文件读取30M
            if not data:
                print('文件全部读取完毕')
                break
            check.update(data)
            check_value = check.hexdigest()
            fileuniquevalue_and_number[check_value] = number
            with open(os.path.join(storage_split_file_path,str(number)),'wb') as fp_temp:
                fp_temp.write(data)
            number += 1
        storage_file_info(storage_split_file_path,fileuniquevalue_and_number)


def storage_file_info(storage_split_file_path,fileuniquevalue_and_number):
    '''将生成的文件排序名及效验值的字典保存为json'''
    with open(os.path.join(storage_split_file_path,JSONNAME),'w') as fp_json:
        fp_json.write(json.dumps(fileuniquevalue_and_number))
    print('保存json成功')

def recv_welcome(cli_socket):
    welcome = cli_socket.recv(1024)
    print(welcome)


def socket_bind():
    try:
        cli_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cli_socket.connect(ADDR)
    except socket.error as msg:
        print('socket_client() error: ' + msg)
        sys.exit(1)

    return cli_socket

if __name__ == '__main__':
    cloud_client()