# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy import ForeignKey
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class CtiStatus(Base):

    __tablename__ = 'ctistatus'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('presence_id', 'name'),
    )

    id = Column(Integer)
    presence_id = Column(Integer, ForeignKey('ctipresences.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    actions = Column(String(255))
    color = Column(String(20))
    access_status = Column(String(255))
    deletable = Column(Integer)
