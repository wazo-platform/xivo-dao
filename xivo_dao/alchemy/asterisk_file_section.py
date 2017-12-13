# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class AsteriskFileSection(Base):

    __tablename__ = 'asterisk_file_section'
    __table_args__ = (
        UniqueConstraint('name', 'asterisk_file_id'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    priority = Column(Integer)
    asterisk_file_id = Column(Integer,
                              ForeignKey('asterisk_file.id', ondelete='CASCADE'),
                              nullable=False)
