# coding=utf-8

import re
import hmac
import json
import base64
import hashlib
import random
import string
import binascii
import logging
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA, SHA256
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA

import settings


# 解决Incorrect padding错误
def decode_base64(data):
    # data = bytes(data.encode())
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.urlsafe_b64decode(data)


# base64
def encode_base64(data):
    value = base64.urlsafe_b64encode(data)
    return value.strip(b"=").decode()


# SHA256
def build_sha256(data):
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(data.encode())
    return hash_sha256.hexdigest()


def build_encodekey():
    randomstr = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    rsakey = RSA.importKey(base64.urlsafe_b64decode(settings.get("AICONF").get("PUBLIC_KEY")))
    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
    encodekey = base64.urlsafe_b64encode(cipher.encrypt(randomstr.encode())).decode()
    return randomstr, encodekey


def build_sign(data):
    keys = list(data.keys())
    keys.sort()
    sign = ''
    for key in keys:
        if not data[key]:
            continue
        if sign:
            sign += "&"
        sign += "{}={}".format(key, data[key])
    sign_sha256 = build_sha256(sign)
    return sign_sha256


def build_authinfo(uri, verb, sign, timestamp):
    str_to_sign = '{uri},{verb},{sign},{timestamp}'.format(uri=uri, verb=verb, sign=sign, timestamp=timestamp)
    signature = hmac.new(settings.get("AICONF").get("SECRET_KEY").encode(), str_to_sign.encode(), digestmod=hashlib.sha1).hexdigest().upper()
    once = hash(hex(timestamp) + settings.get("AICONF").get("LocalIP"))
    authorization = '{once}:{timestamp}:{AK}:{sign}'.format(once=once, timestamp=timestamp, AK=settings.get("AICONF").get("ACCESS_KEY"), sign=signature)
    authorization_base64 = (base64.urlsafe_b64encode(authorization.encode())).decode()
    return authorization_base64


class AESECB:
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_ECB
        self.bs = 16  # block size
        self.PADDING = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def encrypt(self, text):
        generator = AES.new(self.key, self.mode)  # ECB模式无需向量iv
        crypt = generator.encrypt((self.PADDING(text)).encode())
        crypted_str = base64.b64encode(crypt)
        result = crypted_str.decode()
        return result

    def decrypt(self, text):
        try:
            generator = AES.new(self.key, self.mode)  # ECB模式无需向量iv
            text += (len(text) % 4) * '='
            decrpyt_bytes = base64.b64decode(text)
            meg = generator.decrypt(decrpyt_bytes)
            # 去除解码后的非法字符
            result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', meg.decode())
        except Exception as e:
            print(e)
            raise e
        return result


# 为了确保传输的数据没有被篡改，一般会给出文件的crc32、md5或sha1
# crc32
def get_crc32(filename):
    with open(filename, 'rb') as f:
        return binascii.crc32(f.read())


def get_block_crc32(filepath, startoffset, endoffset):
    length = endoffset - startoffset
    with open(filepath, 'rb') as f:
        f.seek(startoffset)
        data = f.read(length)
        crc32 = binascii.crc32(data)
    return data, crc32


# RSA
# 生成密钥对(公钥和私钥)
# 私钥解密
# 公钥加密
# 获取私钥
# 获取公钥


class RSAUtil(object):
    def __init__(self):
        self.public_key = base64.urlsafe_b64decode(settings.get("AICONF").get("PUBLIC_KEY"))

    def generate_key(self):
        # 伪随机数生成器
        random_generator = Random.new().read
        self.key = random_generator
        # rsa算法生成实例
        rsa = RSA.generate(1024, random_generator)

        private_pem = rsa.exportKey()
        public_pem = rsa.publickey().exportKey()
        return public_pem, private_pem

    def encrypt(self, msg, public_key=None, length=117):
        """
        RSA加密
        单次加密串的长度最大为 (key_size/8)-11
        1024bit的证书用117， 2048bit的证书用 260
        :param msg: str
        :param length: int
        :return : str base64编码
        """
        if not public_key:
            public_key = self.public_key
        msg = msg.encode()
        rsakey = RSA.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        res = []
        for i in range(0, len(msg), length):
            res.append(cipher.encrypt(msg[i:i + length]))
        value = b"".join(res)
        cipher_text = encode_base64(value)
        return cipher_text.decode()

    def decrypt(self, msg, private_key=None, length=128):
        """
        RSA解密
        1024bit的证书用128，2048bit证书用256位
        """
        msg = decode_base64(msg.encode())
        rsakey = RSA.importKey(private_key)
        cipher = PKCS1_OAEP.new(rsakey)
        res = []
        for i in range(0, len(msg), length):
            res.append(cipher.decrypt(msg[i:i + length], self.key))
        value = b"".join(res)
        return value.decode()

    def signature(self, msg, private_key=None):
        """私钥加签"""

        msg = msg.encode()
        rsakey = RSA.importKey(private_key)
        signer = Signature_pkcs1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(msg)
        sign = signer.sign(digest)
        signature = base64.b64encode(sign)
        return signature.decode()

    def is_verify(self, msg, signature):
        """公钥验签"""
        msg = msg.encode()
        rsakey = RSA.importKey(self.public_key)
        verifier = Signature_pkcs1_v1_5.new(rsakey)
        digest = SHA256.new()
        # Assumes the data is base64 encoded to begin with
        digest.update(msg)
        is_verify = verifier.verify(digest, base64.b64decode(signature))
        return is_verify


# AES
# 生成密钥(AES密钥长度为128位、192位、256位)
# 二进制转十六进制
# 加密
# 解密


class AesUtil(object):
    def __init__(self, key):
        self.key = key.encode()
        self.mode = AES.MODE_ECB
        self.padding = '\0'


    # 加密函数，加密文本text必须为16的倍数！
    def encrypt(self, text):
        pad = lambda s: s + (16 - len(s) % 16) * self.padding
        cryptor = AES.new(self.key, self.mode)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        # java PKCS5Padding是怎么填充的
        text = pad(text)

        self.ciphertext = cryptor.encrypt(text.encode())
        value = encode_base64(self.ciphertext)
        return value.decode()

    # 解密
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode)
        plain_text = cryptor.decrypt(base64.urlsafe_b64decode(text))
        value = plain_text.decode()
        return value.rstrip(self.padding)


if __name__ == '__main__':
    message = 'hello ghost, this is a plian text'
    rsa = RSAUtil()
    public_key, private_key = rsa.generate_key()
    e = rsa.encrypt(message, public_key=public_key)
    print(e)
    d = rsa.decrypt(e, private_key=private_key)
    print(d)

    # e = rsa.signature(message, private_key)
    # print(e)
    # d = rsa.is_verify(message, e, public_key)
    # print(d)