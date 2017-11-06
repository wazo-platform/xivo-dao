# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import uuid

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, ForeignKeyConstraint,\
    UniqueConstraint
from sqlalchemy.types import Integer, String, Enum, Text

from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base


def _new_uuid():
    return str(uuid.uuid4())


class User(Base):

    __tablename__ = 'user'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('login', 'meta'),
        UniqueConstraint('uuid'),
    )

    id = Column(Integer, nullable=False)
    uuid = Column(String(38), nullable=False, default=_new_uuid, server_default=text('uuid_generate_v4()'))
    entity_id = Column(Integer)
    login = Column(String(64), nullable=False, server_default='')
    passwd = Column(String(64), nullable=False, server_default='')
    meta = Column(Enum('user',
                       'admin',
                       'root',
                       name='user_meta',
                       metadata=Base.metadata),
                  nullable=False, server_default='user')
    valid = Column(Integer, nullable=False, server_default='1')
    time = Column(Integer, nullable=False, server_default='0')
    dcreate = Column(Integer, nullable=False, server_default='0')
    dupdate = Column(Integer, nullable=False, server_default='0')
    obj = Column(Text, nullable=False, default='')

    entity = relationship(Entity)
