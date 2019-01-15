# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class StatQueue(Base):

    __tablename__ = 'stat_queue'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('stat_queue__idx_name', 'name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
