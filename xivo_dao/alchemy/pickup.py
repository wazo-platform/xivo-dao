# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Text

from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.orm import relationship


class Pickup(Base):

    __tablename__ = 'pickup'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('name')
    )

    id = Column(Integer, nullable=False, autoincrement=False)
    entity_id = Column(Integer)
    name = Column(String(128), nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    entity = relationship(Entity)
