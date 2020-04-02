# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.types import (
    Integer,
    String,
    Boolean,
)

from xivo_dao.helpers.db_manager import Base


class Conference(Base):

    __tablename__ = 'conference'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

    id = Column(Integer)
    tenant_uuid = Column(String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False)
    name = Column(String(128))
    preprocess_subroutine = Column(String(39))

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
    )
