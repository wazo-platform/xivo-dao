# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer

from xivo_dao.helpers.db_manager import Base


class StatsConfAgent(Base):

    __tablename__ = 'stats_conf_agent'
    __table_args__ = (
        PrimaryKeyConstraint('stats_conf_id', 'agentfeatures_id'),
    )

    stats_conf_id = Column(Integer, nullable=False, autoincrement=False)
    agentfeatures_id = Column(Integer, nullable=False, autoincrement=False)
