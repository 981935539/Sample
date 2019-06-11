# coding=utf-8

import time
import json
import logging
import requests
import tornado.gen
import tornado.httpclient
from urllib import parse
from queue import Empty

import settings
from db import AIScreeningInfo, connect_db
from .common import encry_and_sign
from .encryption import build_authinfo


def save_patientinfo(serialUID, msg, code, data=None, type=0):
    """保存病例信息，0:outpatient, 1: get_ai_analyse, 2:get_ai_result"""
    db_session = connect_db(settings.get("DATABASE").get("rispacs"))
    try:
        if type == 0:
            patient = db_session.query(AIScreeningInfo).filter_by(seriesuuid=serialUID).one()
            patient.outpatient_state = code
            patient.outpatient_msg = msg
        elif type == 1:
            patient = db_session.query(AIScreeningInfo).filter_by(seriesuuid=serialUID).one()
            patient.aianalyse_msg = msg
        else:
            patient = db_session.query(AIScreeningInfo).filter_by(seriesuuid=serialUID).one()
            patient.airesult_state = code
            patient.airesult_msg = msg
            patient.airesults = data
        db_session.commit()
    except Exception as e:
        logging.exception(e)
        db_session.rollback()
    finally:
        db_session.close()


# @tornado.gen.coroutine
def upload_patient(pacsimage):
    """上传病例"""
    try:
        code = 0  # 默认为0未上传，1成功，-1失败
        msg = ""
        logging.info("上传病例: seriesUID:{}".format(pacsimage[0]["serialUID"]))
        ts = int(time.time() * 1000)
        data = {"pacsImages": pacsimage}
        request_data, sign_sha256 = encry_and_sign(data, ts)

        # build auth
        authinfo = build_authinfo(uri=settings.get("APICONF").get("API_OUT_PATIENT"), verb='POST', sign=sign_sha256, timestamp=ts)
        url_result = parse.urljoin(settings.get("URL").get("AISERVER_URL"), settings.get("APICONF").get("API_OUT_PATIENT"))

        res = requests.post(url_result, data=request_data, headers={'Authorization': authinfo})
        if res.status_code != 200:
            code = -1 if res.status_code != 599 else 0
            msg = "[{}], {}".format(res.status_code, res.reason)
            logging.error("上传病例信息失败：[{}]:{}".format(res.status_code, res.reason))
        else:
            result = res.json()
            code = 1 if result.get("code", "") == "000000" else -1
            msg = "[{}], msg:{}".format(code, result.get("msg", ""))
            logging.info("上传病例完成:[{}], msg:{}".format(code, msg))
        save_patientinfo(pacsimage[0]["serialUID"], msg, code)
    except Exception as e:
        logging.exception(e)


def get_ai_analyse(seriesUID):
    """发起ai请求分析"""
    try:
        ts = int(time.time() * 1000)
        data = {'serialUID': seriesUID, 'type': 0, 'priority': 'normal'}

        request_data, sign_sha256 = encry_and_sign(data, ts)
        print('request_data', request_data)

        # build auth
        authinfo = build_authinfo(uri=settings.get("APICONF").get("API_REQUEST_AI"), verb='POST', sign=sign_sha256, timestamp=ts)
        url_result = parse.urljoin(settings.get("URL").get("AISERVER_URL"), settings.get("APICONF").get("API_REQUEST_AI"))
        res = requests.post(url_result, data=request_data, headers={'Authorization': authinfo})
        if res.status_code != 200:
            logging.error("发起AI请求分析失败：[{}]:{}".format(res.status_code, res.reason))
            return
        result = res.json()
        msg = result["msg"]
        print(msg)
        save_patientinfo(None, msg, type=1)
    except Exception as e:
        logging.exception(e)


def select_ai_result(seriesUID):
    """获取AI分析结果"""
    try:
        data = ""
        code = 0
        msg = ""
        ts = int(time.time() * 1000)
        data = {'serialUID': seriesUID, 'type': 0}
        request_data, sign_sha256 = encry_and_sign(data, ts)
        # build auth
        authinfo = build_authinfo(uri=settings.get("APICONF").get("API_REQUEST_AI_RESULT"), verb='POST', sign=sign_sha256, timestamp=ts)

        url_result = parse.urljoin(settings.get("URL").get("AISERVER_URL"), settings.get("APICONF").get("API_REQUEST_AI_RESULT"))
        res = requests.post(url_result, data=request_data, headers={'Authorization': authinfo})
        if res.status_code != 200:
            code = -1 if res.status_code != 599 else 0
            msg = "[{}], {}".format(res.status_code, res.reason)
            logging.error("获取AI分析结果失败：[{}]:{}".format(res.status_code, res.reason))
        else:
            result = res.json()
            msg = result.get("msg", "")
            res_code = result.get('code', "")
            if res_code == "000000":
                code = 1
            elif res_code == "003006":
                code = 0
            else:
                code = -1
            data = result.get("data", '')
            msg = "[{}], msg:{}".format(res_code, msg)
            logging.info("获取AI分析结果: result:{}".format(result))
        save_patientinfo(seriesUID, msg, code, data=json.dumps(data), type=2)
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    upload_patient()