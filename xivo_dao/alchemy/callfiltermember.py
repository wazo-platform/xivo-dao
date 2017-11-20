# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, UniqueConstraint, CheckConstraint
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.alchemy import enum
from xivo_dao.helpers.db_manager import Base


class Callfiltermember(Base):

    __tablename__ = 'callfiltermember'
    __table_args__ = (
        UniqueConstraint('callfilterid', 'type', 'typeval'),
        CheckConstraint("bstype in ('boss', 'secretary')")
    )

    id = Column(Integer, primary_key=True)
    callfilterid = Column(Integer, nullable=False, server_default='0')
    type = Column(Enum('user',
                       name='callfiltermember_type',
                       metadata=Base.metadata),
                  nullable=False)
    typeval = Column(String(128), nullable=False, server_default='0')
    ringseconds = Column(Integer, nullable=False, server_default='0')
    priority = Column(Integer, nullable=False, server_default='0')
    bstype = Column(enum.generic_bsfilter, nullable=False)
    active = Column(Integer, nullable=False, server_default='0')
