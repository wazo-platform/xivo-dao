# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.uuid import new_uuid


class MOH(Base):

    __tablename__ = 'moh'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('name'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    name = Column(Text, nullable=False)
    label = Column(Text)
    mode = Column(Text, nullable=False)
    application = Column(Text)
    sort = Column(Text)
