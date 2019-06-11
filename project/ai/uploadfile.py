# coding=utf-8

import os
import json
import time
import logging
from datetime import datetime
from urllib import parse
import tornado.httpclient
import tornado.gen

import settings
from .common import encry_and_sign
from db import connect_db, AIScreeningInfo
from .encryption import get_crc32, build_authinfo, get_block_crc32


def build_partition(uploadinfo):
    """分片及分片信息"""
    upload_blockinfo_list = []
    if uploadinfo["fileSize"] <= settings.PARTITION_SIZE:
        blockinfo = uploadinfo.copy()
        blockinfo["startOffset"] = 0
        blockinfo["endOffset"] = uploadinfo["fileSize"]
        upload_blockinfo_list.append(blockinfo)
    else:
        filesize = uploadinfo["fileSize"]
        partition_size = settings.PARTITION_SIZE
        partition_count = int(filesize / partition_size)
        last_partition_size = filesize % partition_size
        print("filesize:{},partion_size:{}, partition_count:{}, last:{}".format(filesize, partition_size, partition_count, last_partition_size))

        for i in range(partition_count):
            blockinfo = uploadinfo.copy()
            blockinfo["startOffset"] = i * partition_size
            blockinfo["endOffset"] = (i+1) * partition_size
            upload_blockinfo_list.append(blockinfo)

        if last_partition_size > 0:
            blockinfo = uploadinfo.copy()
            blockinfo["startOffset"] = partition_count * partition_size
            blockinfo["endOffset"] = blockinfo["startOffset"] + last_partition_size
            upload_blockinfo_list.append(blockinfo)
    return upload_blockinfo_list


def save_uploadinfo(serialUID, uploadinfo, upload_state, code, errordesc):
    """保存上传文件信息"""
    db_session = connect_db(settings.get("DATABASE").get("rispacs"))
    try:
        patient = db_session.query(AIScreeningInfo).filter_by(seriesuuid=serialUID).one()
        patient.uploadinfo = json.dumps(uploadinfo)
        patient.upload_code = code
        patient.upload_state = upload_state
        patient.aiupload_msg = errordesc
        patient.uploadtime = datetime.today()
        db_session.commit()
    except Exception as e:
        logging.exception(e)
        db_session.rollback()
    finally:
        db_session.close()

# @func_timer
async def async_upload_file(serialUID, filepath, upload_blockinfo):
    """异步上传文件"""
    ts = int(time.time() * 1000)
    # 计算分片CRC32
    data, crc32 = get_block_crc32(filepath, upload_blockinfo["startOffset"], upload_blockinfo["endOffset"])
    upload_blockinfo['dataCRC32'] = crc32

    # 数据加密和签名
    request_data, sign_sha256 = encry_and_sign(upload_blockinfo, ts)

    uri_path = settings.get("APICONF").get("API_FILE_UPLOAD") + serialUID
    url = parse.urljoin(settings.get("URL").get("AI_UPLOAD_SERVER_URL"), uri_path)
    # build auth
    authinfo = build_authinfo(uri=uri_path, verb='POST', sign=sign_sha256, timestamp=ts)
    headers = {"Authorization": authinfo, "uploadInfo": json.dumps(request_data),
               "Content-Type": settings.Content_Type}

    client = tornado.httpclient.AsyncHTTPClient()
    request = tornado.httpclient.HTTPRequest(url, method="POST", body=data, headers=headers, validate_cert=False)
    res = await client.fetch(request, raise_error=False)
    return res


async def upload_file(serialUID, uploadinfo):
    """文件上传"""
    upload_state = 0
    errordesc = ""
    code = ""
    try:
        filepath = os.path.join(settings.get("FILEPATH")["ai"]["compress"], uploadinfo["fileName"])
        # 判断文件是否存在
        if not os.path.exists(filepath):
            upload_state = -1
            logging.error(u"文件不存在！，serialUID: [{}]".format(serialUID))
            errordesc = "file not exists"
            save_uploadinfo(serialUID, uploadinfo, upload_state, code, errordesc)
            return

        # 获取文件大小
        file_size = os.path.getsize(filepath)
        uploadinfo["fileSize"] = file_size
        if file_size <= 0:
            upload_state = -1
            logging.error(u"文件为空！，serialUID: [{}]".format(serialUID))
            errordesc = "file is empty"
            save_uploadinfo(serialUID, uploadinfo, upload_state, code, errordesc)
            return

        # 计算CRC32
        uploadinfo["fileCRC32"] = get_crc32(filepath)

        # 生成分片信息
        upload_blockinfo_list = build_partition(uploadinfo)

        size = 1
        # 上传文件
        for upload_blockinfo in upload_blockinfo_list:
            logging.info("开始上传分片[{}], startoffset:[{}], endoffset:[{}]".format(size, upload_blockinfo["startOffset"], upload_blockinfo["endOffset"]))
            res = await async_upload_file(serialUID,filepath, upload_blockinfo)
            if res.code != 200:
                upload_state = -1 if res.code != 599 else 0
                errordesc = "[{}]{}".format(res.code, res.reason)
                logging.error(u'AI上传文件失败,serialUID:[{}], error:{}'.format(serialUID, errordesc))
                break
            else:
                result = json.loads(res.body)
                print(result)
                if result["code"] == "000000":
                    logging.info(
                        "上传成功分片[{}], startoffset:[{}], endoffset:[{}]".format(size, upload_blockinfo["startOffset"],
                                                                              upload_blockinfo["endOffset"]))

                    upload_state = 1
                    code = result.get("code", "")
                    errordesc = "[{}], msg:{}".format(code, result.get("msg", ""))
                elif result["code"] == "001010":
                    size += 1
                    continue
                else:
                    upload_state = -1
                    logging.info(u"AI上传文件失失败, serialUID:[{}], result: {}".format(serialUID, result))
                    code = result.get("code", "")
                    errordesc = "[{}], msg:{}".format(code, result.get("msg", ""))
                    break
            size += 1
        if upload_state == 1:
            logging.info(u"AI上传文件成功, serialUID:[{}]".format(serialUID))
        # 删除上传文件
        os.remove(filepath)
        save_uploadinfo(serialUID, uploadinfo, upload_state, code, errordesc)
    except Exception as e:
        logging.exception(e)
        errordesc = "[{}]{}".format(e.__class__.__name__, str(e))
        save_uploadinfo(serialUID, uploadinfo, upload_state, code, errordesc)


if __name__ == '__main__':
    upload_file("2d32e4b631e03e53aef060d50211c298")
