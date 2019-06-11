# coding=utf-8

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ImageStoragePathMap = {'srcdir':'/dx', '../tests/volume':'C:\\Users\\Administrator\\Desktop'}

def dir_exist(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

DEBUG = False
PORT = 8085
PROCESS_NUM = 0   # 进程数

# 日志配置
LOGCONF = {
    "dir": "/var/log/webpacsai",
    "name": "main",
    "level": "DEBUG",
    "backcount": 10
}

# 数据库配置
DATABASE = {
    "hyx": {
        'host': '10.119.43.84',
        'user': 'postgres',
        'passwd': '123456',
        'dbname': 'test',
        'encoding': 'utf8',
        'echo': False
    },
    "rispacs": {
        'host': '10.11.12.148',
        'user': 'postgres',
        'passwd': '123456',
        'dbname': 'test',
        'encoding': 'utf8',
        'echo': False
    }
}


# 文件路径配置
FILEPATH = {
    "ai": {
        "compress": dir_exist(os.path.join(BASE_DIR, 'data/ai/compress')),
        "failed": dir_exist(os.path.join(BASE_DIR, 'data/ai/failed')),
    },
    "study": {
            "compress": dir_exist(os.path.join(BASE_DIR, 'data/study/compress')),
            "failed": dir_exist(os.path.join(BASE_DIR, 'data/study/failed')),
    },
    "report": {
            "compress": dir_exist(os.path.join(BASE_DIR, 'data/report/compress')),
            "failed": dir_exist(os.path.join(BASE_DIR, 'data/report/failed')),
            "backups": dir_exist(os.path.join(BASE_DIR, 'data/report/backups'))
    }
}

SFTP = {
    "host": "118.25.42.235",
    "port": 22,
    "username": "root",
    "password": "yang1687.",
    # "local": 'F:\\sftptest\\aaa\\test.py', # 本地目录或文件
    "remote": "/data/sftptest/" # 远程目录
}

PARTITION_SIZE = 8*1024*1024    # 8M
Content_Type = "application/octet-stream"  # HTTP请求内容类型
IF_AISERVER = True
IF_INCREASE_STUDY = True
IF_INCREASE_REPORT = True

URL = {
    "AISERVER_URL": "http://14.116.177.132:8004",  # 测试服务器地址
    "AI_UPLOAD_SERVER_URL": "http://14.116.177.132:8001"
}


# Ai相关配置信息
AICONF = {
    "CHANNEL_ID": "0000060000",  # 渠道ID
    "ORGANIZATION_ID": "003131010100000080000000",  # 数据机构ID
    "ACCESS_KEY": "maOG6iWpvEzk82n5D2R27b4HRUJeC1CjHPjks-MNWQ1TisOi6qoeB5Sqkq8yDOJEPe249_knqzWp00qNCjopJDagMsvZ43kUCVyiGpjfO-_r4cDhXBXZWrjwewQgSUBYjszyf7pjwDWOEn8px6VP6qLMwOkgkH3dxQ9ISH8v2Gg",
    "SECRET_KEY": "fuI2fFyf3_ny4WeKxUYyfry2MT5VpgYSYXvBz3MXqFEIpNAva2K3BCVTkr15mpwKFjpm9WrxLK0q0YYbfIqtkDfdqDQHJ_LFCbNMsgtEgaOQvvF6JrwbD2LUGOCH_1cFZW5ChPYxGOnaoVD2bnyeJ_bZXxNQd0Avv84NMnFUmcs",
    "PUBLIC_KEY": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCcaCXOnMlSaPGjYJGUsvC0gYyBuUIllY3HrcuTTC0_YXcEKYWxvbD56J_XtngtccW_KGxBlDkdqobPm1tHYV9mxqBaOGkFod47Yvf1TVTvMY1rmRgBMQP5DhL1emj-etQHtivq2iXLosqfSE1UmSKN69f1lQVC_8yYem1gG4FWmQIDAQAB",
    "LocalIP": '10.11.12.91',
    "DeviceID": '00:00:00:00:00:00',
}

# API相关配置
APICONF = {
    "API_VERSION": "1.1",  # API版本
    "API_REQUEST_AI": "/api/ai/request",  # 发起AI请求
    "API_REQUEST_AI_RESULT": "/api/ai/result",  # 获取AI结果
    "API_OUT_PATIENT": '/api/patient/outPatient', # 门诊患者信息
    "API_FILE_UPLOAD": "/fileupload/data/serialUID=",  # 文件地址
}

# 加密相关配置
ENCRYP = {
    "SIGN_METHOD": "sha256",
    "ALGORITHM_KEY": "AES",  # 密钥算法
    "ALGORITHM_ECB": "AES/ECB/PKCS5Padding",  # 加密算法/工作模型/填充模式
}

get = lambda key, default=dict(): sys.modules[__name__].__dict__.get(key, default)
