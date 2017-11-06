# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, ForeignKeyConstraint
from sqlalchemy.types import DateTime, Integer, Text, UnicodeText

from xivo_dao.helpers.db_manager import Base


class CEL(Base):

    __tablename__ = 'cel'
    __table_args__ = (
        ForeignKeyConstraint(('call_log_id',),
                             ('call_log.id',),
                             ondelete='SET NULL'),
        Index('cel__idx__call_log_id', 'call_log_id'),
        Index('cel__idx__eventtime', 'eventtime'),
        Index('cel__idx__linkedid', 'linkedid'),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    eventtype = Column(Text, nullable=False)
    eventtime = Column(DateTime, nullable=False)
    userdeftype = Column(Text, nullable=False)
    cid_name = Column(UnicodeText, nullable=False)
    cid_num = Column(UnicodeText, nullable=False)
    cid_ani = Column(Text, nullable=False)
    cid_rdnis = Column(Text, nullable=False)
    cid_dnid = Column(Text, nullable=False)
    exten = Column(UnicodeText, nullable=False)
    context = Column(Text, nullable=False)
    channame = Column(UnicodeText, nullable=False)
    appname = Column(Text, nullable=False)
    appdata = Column(Text, nullable=False)
    amaflags = Column(Integer, nullable=False)
    accountcode = Column(Text, nullable=False)
    peeraccount = Column(Text, nullable=False)
    uniqueid = Column(Text, nullable=False)
    linkedid = Column(Text, nullable=False)
    userfield = Column(Text, nullable=False)
    peer = Column(Text, nullable=False)
    extra = Column(Text)
    call_log_id = Column(Integer)

    call_log = relationship('CallLog')
