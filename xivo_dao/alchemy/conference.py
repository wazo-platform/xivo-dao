# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.sql import cast, select
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.helpers.db_manager import Base

from .extension import Extension


class Conference(Base):
    __tablename__ = 'conference'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('conference__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128))
    preprocess_subroutine = Column(String(79))

    max_users = Column(Integer, nullable=False, server_default='50')
    record = Column(Boolean, nullable=False, server_default='False')

    pin = Column(String(80))
    quiet_join_leave = Column(Boolean, nullable=False, server_default='False')
    announce_join_leave = Column(Boolean, nullable=False, server_default='False')
    announce_user_count = Column(Boolean, nullable=False, server_default='False')
    announce_only_user = Column(Boolean, nullable=False, server_default='True')
    music_on_hold = Column(String(128))

    admin_pin = Column(String(80))

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'conference',
                            Extension.typeval == cast(Conference.id, String))""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    incall_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.category == 'incall',
                            Dialaction.action == 'conference',
                            Dialaction.actionarg1 == cast(Conference.id, String))""",
        foreign_keys='Dialaction.actionarg1',
        viewonly=True,
    )

    incalls = association_proxy('incall_dialactions', 'incall')

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.action == 'conference',
                            Dialaction.actionarg1 == cast(Conference.id, String))""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
        overlaps='_dialaction_actions',
    )

    func_keys_conference = relationship(
        'FuncKeyDestConference',
        cascade='all, delete-orphan',
    )

    @hybrid_property
    def exten(self):
        for extension in self.extensions:
            return extension.exten
        return None

    @exten.expression
    def exten(cls):
        return (
            select(Extension.exten)
            .where(Extension.type == 'conference')
            .where(Extension.typeval == cast(cls.id, String))
            .scalar_subquery()
        )
