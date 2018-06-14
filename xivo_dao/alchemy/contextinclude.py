# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class ContextInclude(Base):

    __tablename__ = 'contextinclude'

    context = Column(String(39), primary_key=True)
    include = Column(String(39), primary_key=True)
    priority = Column(Integer, nullable=False, server_default='0')

    included_context = relationship(
        'Context',
        primaryjoin='Context.name == ContextInclude.include',
        foreign_keys='ContextInclude.include',
        uselist=False,
    )
