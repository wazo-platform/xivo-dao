# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiPhoneHints(Base):

    __tablename__ = 'ctiphonehints'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer, nullable=False)
    idgroup = Column(Integer)
    number = Column(String(8))
    name = Column(String(255))
    color = Column(String(128))
