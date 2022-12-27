# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, PrimaryKeyConstraint, Index
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.helpers.db_manager import Base


class StatQueue(Base):

    __tablename__ = 'stat_queue'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('stat_queue__idx_name', 'name'),
        Index('stat_queue__idx_tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    tenant_uuid = Column(String(36), nullable=False)
    queue_id = Column(Integer)
    deleted = Column(Boolean, nullable=False, server_default='false')
