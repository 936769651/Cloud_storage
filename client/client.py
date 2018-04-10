# _*_ coding=utf-8 _*_

'''
send.py
socket client
'''

import socket
import os
import sys
import struct
import time
import hashlib
import json

ADDR = ('192.168.1.103',7000)
#ADDR = ('127.0.0.1',7000)
FILEPATH = r'E:\service\mv.rmvb'
CHUNKSIZE = 1024*1024*30        #每块文件30M

def cloud_client():
    #cli_socket = socket_bind()
    #recv_welcome(cli_socket)
    deal_file(FILEPATH)
    #cli_socket.close()
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


def deal_file(filepath):
    '''开始处理文件'''
    if not os.path.exists(filepath) or not os.path.isfile(filepath):    #如果该路径不存在或不是文件，则退出
        print('{0} 该文件不符合条件，请检查'.format(filepath))
        return
    parent_path = os.path.split(filepath)[0]
    folder_name = '.' + str(int(time.time()))   #以时间戳作为临时文件夹名字
    storage_split_file_path = os.path.join(parent_path,folder_name)
    os.mkdir(storage_split_file_path)
    split_file(filepath,storage_split_file_path)

def split_file(filepath,storage_split_file_path):
    '''分割文件，并生成小文件排序名及各自的效验值'''
    number_and_sha1 = dict()
    number = 0
    sha_obj = hashlib.sha256()
    with open(filepath,'rb') as parent_file:
        while True:
            data = parent_file.read(CHUNKSIZE)   #从文件读取30M
            if not data:
                print('文件全部读取完毕')
                break
            sha_obj.update(data)
            sha_value = sha_obj.hexdigest()
            number_and_sha1[str(number)] = sha_value
            with open(os.path.join(storage_split_file_path,str(number)),'wb') as fp_temp:
                fp_temp.write(data)
            number += 1
        storage_file_info(storage_split_file_path,number_and_sha1)


def storage_file_info(storage_split_file_path,number_and_sha1):
    '''将生成的文件排序名及效验值的字典保存为json'''
    with open(os.path.join(storage_split_file_path,'.file_data.json'),'w') as fp_json:
        fp_json.write(json.dumps(number_and_sha1))
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