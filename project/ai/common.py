# coding=utf-8

import time
import os
import json
import uuid
import socket
import logging
import zipfile
from functools import wraps

import settings
from .encryption import AESECB, build_sign, build_encodekey


# 获取本机mac地址
def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac


# 获取本机IP地址
def get_ip_address():
    #  获取本机电脑名
    myname = socket.getfqdn(socket.gethostname())
    # 获取本机ip
    myaddr = socket.gethostbyname(myname)
    return myaddr


# 获取毫秒单位的时间戳
def get_timestamp():
    t = time.time()
    return int(t*1000)


request_param = {
    "institutionId": settings.get("AICONF").get("ORGANIZATION_ID"),
    "channelId": settings.get("AICONF").get("CHANNEL_ID"),
    "requestId": str(uuid.uuid4()),
    "version": settings.get("APICONF").get("API_VERSION"),
    "deviceId": settings.get("AICONF").get("DeviceID"),
    "deviceIp": settings.get("AICONF").get("LocalIP"),
    "signMethod": "sha256",
    "timestamp": "",
    "sign": '',
    "encodeData": '',
    "encodeKey": ''
}


def encry_and_sign(upload_blockinfo, ts):
    # 生成RSA key
    rsakey, encodekey = build_encodekey()

    # 请求数据加密
    cryptor = AESECB(rsakey.encode())
    encodeData = cryptor.encrypt(json.dumps(upload_blockinfo))

    request_data = request_param.copy()
    request_data['encodeData'] = encodeData
    request_data['encodeKey'] = encodekey
    request_data['timestamp'] = ts
    request_data['requestId'] = str(uuid.uuid4())
    sign_sha256 = build_sign(request_data)
    request_data['sign'] = sign_sha256
    return request_data, sign_sha256


def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        logging.info('[Function: {name} start...]'.format(name = function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logging.info('[Function: {name} finished, spent time: {time:.2f}s]'.format(name = function.__name__,time = t1 - t0))
        return result
    return function_timer


def zip_file(zipfile_path, filepath):
    """zip压缩文件"""
    filelist = os.listdir(filepath)
    with zipfile.ZipFile(zipfile_path, 'w') as f:
        for file in filelist:
            filename = os.path.join(filepath, file)
            f.write(filename, arcname=file)


