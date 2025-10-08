# Copyright 2014-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.feature_extension import FeatureExtension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestAgent(Base):
    DESTINATION_TYPE_ID = 11

    __tablename__ = 'func_key_dest_agent'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id'),
        ForeignKeyConstraint(
            ('func_key_id', 'destination_type_id'),
            ('func_key.id', 'func_key.destination_type_id'),
        ),
        UniqueConstraint('agent_id', 'feature_extension_uuid'),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
        Index('func_key_dest_agent__idx__agent_id', 'agent_id'),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default=f"{DESTINATION_TYPE_ID}")
    agent_id = Column(
        Integer, ForeignKey('agentfeatures.id', ondelete='CASCADE'), nullable=False
    )
    feature_extension_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey('feature_extension.uuid', ondelete='CASCADE'),
        nullable=False,
    )

    type = 'agent'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)
    agent = relationship(AgentFeatures, viewonly=True)

    feature_extension = relationship(FeatureExtension, viewonly=True)
    feature_extension_feature = association_proxy(
        'feature_extension',
        'feature',
        # Only to keep value persistent in the instance
        creator=lambda _feature: FeatureExtension(feature=_feature),
    )

    def to_tuple(self):
        return (
            ('action', self.action),
            ('agent_id', self.agent_id),
        )

    @hybrid_property
    def action(self):
        ACTIONS = {
            'agentstaticlogin': 'login',
            'agentstaticlogoff': 'logout',
            'agentstaticlogtoggle': 'toggle',
        }
        return ACTIONS.get(
            self.feature_extension_feature, self.feature_extension_feature
        )

    @action.expression
    def action(cls):
        return cls.feature_extension_feature  # only used to pass test

    @action.setter
    def action(self, value):
        TYPEVALS = {
            'login': 'agentstaticlogin',
            'logout': 'agentstaticlogoff',
            'toggle': 'agentstaticlogtoggle',
        }
        self.feature_extension_feature = TYPEVALS.get(value, value)
