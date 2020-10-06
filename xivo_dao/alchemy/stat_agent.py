# -*- coding: utf-8 -*-
# Copyright 2012-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class StatAgent(Base):

    __tablename__ = 'stat_agent'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('stat_agent__idx_name', 'name'),
        Index('stat_agent__idx_tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    tenant_uuid = Column(String(36), nullable=False)
    agent_id = Column(Integer)
