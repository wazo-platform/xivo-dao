# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index,\
    UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class QueueFeatures(Base):

    __tablename__ = 'queuefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('queuefeatures__idx__context', 'context'),
        Index('queuefeatures__idx__number', 'number'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    displayname = Column(String(128), nullable=False)
    number = Column(String(40), nullable=False, server_default='')
    context = Column(String(39))
    data_quality = Column(Integer, nullable=False, server_default='0')
    hitting_callee = Column(Integer, nullable=False, server_default='0')
    hitting_caller = Column(Integer, nullable=False, server_default='0')
    retries = Column(Integer, nullable=False, server_default='0')
    ring = Column(Integer, nullable=False, server_default='0')
    transfer_user = Column(Integer, nullable=False, server_default='0')
    transfer_call = Column(Integer, nullable=False, server_default='0')
    write_caller = Column(Integer, nullable=False, server_default='0')
    write_calling = Column(Integer, nullable=False, server_default='0')
    ignore_forward = Column(Integer, nullable=False, server_default='1')
    url = Column(String(255), nullable=False, server_default='')
    announceoverride = Column(String(128), nullable=False, server_default='')
    timeout = Column(Integer)
    preprocess_subroutine = Column(String(39))
    announce_holdtime = Column(Integer, nullable=False, server_default='0')
    waittime = Column(Integer)
    waitratio = Column(DOUBLE_PRECISION)
