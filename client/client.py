# _*_ coding=utf-8 _*_

'''
send.py
socket client
'''

import socket
import os
import sys
import struct


def socket_client():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(('192.168.1.103',7000))
    except socket.error as msg:
        print('socket_client() error: ' + msg)
        sys.exit(1)

    print(s.recv(1024))


if __name__ == '__main__':
    socket_client()