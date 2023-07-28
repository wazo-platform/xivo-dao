# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.schema import Column, UniqueConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.types import String, Boolean

from xivo_dao.helpers.db_manager import Base, IntAsString
from xivo_dao.helpers.uuid import new_uuid


class FeatureExtension(Base):
    __tablename__ = 'feature_extension'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
        UniqueConstraint('exten'),
        Index('feature_extension__idx__exten', 'exten'),
        Index('feature_extension__idx__feature', 'feature'),
        Index('feature_extension__idx__uuid', 'uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    enabled = Column(Boolean, nullable=False, server_default='true')
    exten = Column(String(40), nullable=False, server_default='')
    feature = Column(IntAsString(255), nullable=False, server_default='')

    def is_pattern(self):
        return self.exten.startswith('_')
