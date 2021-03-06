# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class QueueSkillCat(Base):

    __tablename__ = 'queueskillcat'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
    )

    id = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False, server_default='')
