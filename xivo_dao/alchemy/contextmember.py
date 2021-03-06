# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class ContextMember(Base):

    __tablename__ = 'contextmember'
    __table_args__ = (
        PrimaryKeyConstraint('context', 'type', 'typeval', 'varname'),
        Index('contextmember__idx__context', 'context'),
        Index('contextmember__idx__context_type', 'context', 'type'),
    )

    context = Column(String(39))
    type = Column(String(32))
    typeval = Column(String(128), server_default='')
    varname = Column(String(128), server_default='')
