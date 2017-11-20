# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class StatAgent(Base):

    __tablename__ = 'stat_agent'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('stat_agent__idx_name', 'name'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
