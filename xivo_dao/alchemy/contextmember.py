# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base


class ContextMember(Base):
    __tablename__ = 'contextmember'
    __table_args__ = (
        PrimaryKeyConstraint('context', 'type', 'typeval', 'varname'),
        Index('contextmember__idx__context', 'context'),
        Index('contextmember__idx__context_type', 'context', 'type'),
        ForeignKeyConstraint(
            ('context',),
            ('context.name',),
            ondelete='CASCADE',
        ),
    )

    context = Column(String(79))
    type = Column(String(32))
    typeval = Column(String(128), server_default='')
    varname = Column(String(128), server_default='')
