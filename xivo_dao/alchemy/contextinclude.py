# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class ContextInclude(Base):

    __tablename__ = 'contextinclude'

    context = Column(String(39), primary_key=True)
    include = Column(String(39), primary_key=True)
    priority = Column(Integer, nullable=False, server_default='0')
