# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.helpers.db_manager import Base


class FuncKeyDestAgent(Base):

    DESTINATION_TYPE_ID = 11

    __tablename__ = 'func_key_dest_agent'
    __table_args__ = (
        PrimaryKeyConstraint('func_key_id', 'destination_type_id'),
        ForeignKeyConstraint(['func_key_id', 'destination_type_id'],
                             ['func_key.id', 'func_key.destination_type_id']),
        UniqueConstraint('agent_id', 'extension_id'),
        CheckConstraint(f'destination_type_id = {DESTINATION_TYPE_ID}'),
    )

    func_key_id = Column(Integer)
    destination_type_id = Column(Integer, server_default=f"{DESTINATION_TYPE_ID}")
    agent_id = Column(Integer, ForeignKey('agentfeatures.id'), nullable=False)
    extension_id = Column(Integer, ForeignKey('extensions.id'), nullable=False)

    type = 'agent'

    func_key = relationship(FuncKey, cascade='all,delete-orphan', single_parent=True)
    agent = relationship(AgentFeatures)

    extension = relationship(Extension, viewonly=True)
    extension_typeval = association_proxy(
        'extension', 'typeval',
        # Only to keep value persistent in the instance
        creator=lambda _typeval: Extension(type='extenfeatures',
                                           typeval=_typeval)
    )

    def to_tuple(self):
        return (
            ('action', self.action),
            ('agent_id', self.agent_id),
        )

    @hybrid_property
    def action(self):
        ACTIONS = {'agentstaticlogin': 'login',
                   'agentstaticlogoff': 'logout',
                   'agentstaticlogtoggle': 'toggle'}
        return ACTIONS.get(self.extension_typeval, self.extension_typeval)

    @action.expression
    def action(cls):
        return cls.extension_typeval  # only used to pass test

    @action.setter
    def action(self, value):
        TYPEVALS = {'login': 'agentstaticlogin',
                    'logout': 'agentstaticlogoff',
                    'toggle': 'agentstaticlogtoggle'}
        self.extension_typeval = TYPEVALS.get(value, value)
