# coding: utf-8
import os
from datetime import datetime, date

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


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
        'host': '10.11.12.91',
        'user': 'postgres',
        'passwd': '123456',
        'dbname': 'test',
        'encoding': 'utf8',
        'echo': False
    }
}
def convert_sex(sex):
    if sex == "M" or sex == "MALE":
        sex = "女"
    elif sex == "F" or sex == "FEMALE":
        sex = "男"
    else:
        sex = "未知"
    return sex

def _dt_convert(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        return obj


def to_dict(self, simple=False, convert_datetime=True):
    if simple:
        return {c: _dt_convert(getattr(self, c, None)) for c in self._simple_key}
    return {c.name: _dt_convert(getattr(self, c.name, None)) for c in self.__table__.columns}


def connect_db(param):
    engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}/{3}?client_encoding={4}&connect_timeout=5'.
                           format(param["user"], param["passwd"], param["host"], param["dbname"],
                                  param["encoding"]), echo=param["echo"], pool_size=100, pool_recycle=60)

    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=True, expire_on_commit=False)
    session = scoped_session(session_factory)
    return session


def hyx_report_info():
    """获取新增报告信息"""
    db_session = connect_db(DATABASE.get("hyx"))
    results = []
    today = date.today()
    start_time = datetime(year=today.year, month=today.month, day=(today.day - 1), hour=0)
    end_time = datetime(year=today.year, month=today.month, day=today.day, hour=0)

    reports = db_session.execute("select * from rpt_hosted WHERE status='CHECKED' AND last_update_date BETWEEN '{}' AND '{}'".format(start_time, end_time)).fetchall()
    for report in reports:
        order = db_session.execute("select * from ord_hosted where id={}".format(report.order_id)).fetchone()
        examine = db_session.execute(
            "select * from ris_examine_info WHERE examine_serial_num='{}' and examine_state_value=700".format(report.accession_no)).fetchone()
        if not examine: continue

        data = {
            "name": report.cust_name,
            "age": report.cust_age,
            "birthday": report.cust_birthday,
            "sex": convert_sex(report.sex or ""),  # FEMALE, MALE--> 男
            "patientid": report.patient_id or "",
            "accessionno": str(order.accession_no) if order.accession_no else "",
            "studyuids": order.study_uid or "",
            "clinicdiagnose": report.clinic_diagnosls or "",
            "history": report.clinic_history_desc or "",
            "studyitem": examine.examine_describe or "",
            "studyobseve": report.detall or "",
            "studyresult": report.result or "",
            "studytime": examine.examine_time.strftime("%Y-%m-%d %H:%M:%S") or "",
            "modality": report.modality or "",
        }
        results.append(data)
    print(results)

if __name__ == '__main__':
    hyx_report_info()