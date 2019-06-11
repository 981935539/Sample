# coding: utf-8
import os
from datetime import datetime, date

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base

ECHO = False

if not os.path.exists('sqlite'): os.mkdir('sqlite')
conn_str = "sqlite+pysqlite:///sqlite/agent.db"
# dbengine = create_engine(conn_str, convert_unicode=True, encoding='utf8', echo=ECHO)
dbengine = create_engine(conn_str, convert_unicode=True, encoding='utf8', echo=ECHO, connect_args={'check_same_thread': False})
session_factory = sessionmaker(bind=dbengine, autocommit=False, autoflush=True, expire_on_commit=False)
db_session = scoped_session(session_factory)


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


Base = declarative_base()
Base.query = db_session.query_property()
Base.to_dict = to_dict


def init_db():
    from . import models
    Base.metadata.create_all(bind=dbengine)