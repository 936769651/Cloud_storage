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


def socket_service():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(('0.0.0.0',7000))    #绑定自身所有地址
        s.listen(1)
    except socket.error as msg:
        print('socket_service eroor: ' + msg)
        sys.exit(1)

    print('Waiting connection...')

    while True:
        conn,addr = s.accept()
        t = threading.Thread(target=deal_data,args=(conn,addr))
        t.start()

def deal_data(conn,addr):
    print('Accept new connection from {0}'.format(addr))
    conn.send('Hi,welcome!')

if __name__ == '__main__':
    socket_service()