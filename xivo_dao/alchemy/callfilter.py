# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.alchemy import enum
from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import text


class Callfilter(Base):

    __tablename__ = 'callfilter'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    entity_id = Column(Integer, server_default=text('NULL'))
    name = Column(String(128), nullable=False, server_default='')
    type = Column(enum.callfilter_type, nullable=False)
    bosssecretary = Column(enum.callfilter_bosssecretary)
    callfrom = Column(enum.callfilter_callfrom)
    ringseconds = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    entity = relationship(Entity)
