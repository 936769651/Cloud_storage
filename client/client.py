# _*_ coding=utf-8 _*_

'''
send.py
socket client
'''

import socket
import os
import sys
import struct

ADDR = ('192.168.1.103',7000)
#ADDR = ('127.0.0.1',7000)
FILEPATH = r'E:\1.jpg'

def cloud_client():
    cli_socket = socket_bind()
    recv_welcome(cli_socket)
    if os.path.isfile(FILEPATH):
        fileinfo_size = struct.calcsize('128sd')
        fhead = struct.pack('128sd',os.path.basename(FILEPATH).encode('utf-8'),os.stat(FILEPATH).st_size)
        cli_socket.send(fhead)

        fp = open(FILEPATH,'rb')
        while True:
            data = fp.read(1024)
            if not data:
                print('{0} file send over...'.format(FILEPATH))
                break
            cli_socket.send(data)
        cli_socket.close()

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