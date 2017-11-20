# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Integer, String, Binary

from xivo_dao.helpers.db_manager import Base


class Attachment(Base):

    __tablename__ = 'attachment'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('object_type', 'object_id'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)
    object_type = Column(String(16), nullable=False)
    object_id = Column(Integer, nullable=False)
    file = Column(Binary)
    size = Column(Integer, nullable=False)
    mime = Column(String(64), nullable=False)
