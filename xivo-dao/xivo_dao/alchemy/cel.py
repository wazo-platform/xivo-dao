# -*- coding: UTF-8 -*-

from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from xivo_dao.alchemy.base import Base


class CEL(Base):
    __tablename__ = 'cel'

    id = Column(Integer, primary_key=True)
    eventtype = Column(String(30), nullable=False)
    eventtime = Column(DateTime, nullable=False)
    userdeftype = Column(String(255), nullable=False)
    cid_name = Column(String(80, convert_unicode=True), nullable=False)
    cid_num = Column(String(80, convert_unicode=True), nullable=False)
    cid_ani = Column(String(80), nullable=False)
    cid_rdnis = Column(String(80), nullable=False)
    cid_dnid = Column(String(80), nullable=False)
    exten = Column(String(80, convert_unicode=True), nullable=False)
    context = Column(String(80), nullable=False)
    channame = Column(String(80, convert_unicode=True), nullable=False)
    appname = Column(String(80), nullable=False)
    appdata = Column(String(80), nullable=False)
    amaflags = Column(Integer, nullable=False)
    accountcode = Column(String(20), nullable=False)
    peeraccount = Column(String(20), nullable=False)
    uniqueid = Column(String(150), nullable=False)
    linkedid = Column(String(150), nullable=False)
    userfield = Column(String(255), nullable=False)
    peer = Column(String(80), nullable=False)
