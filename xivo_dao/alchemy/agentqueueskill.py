# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class AgentQueueSkill(Base):

    __tablename__ = 'agentqueueskill'
    __table_args__ = (
        PrimaryKeyConstraint('agentid', 'skillid'),
    )

    agentid = Column(Integer, nullable=False, autoincrement=False)
    skillid = Column(Integer, nullable=False, autoincrement=False)
    weight = Column(Integer, nullable=False, server_default='0')
