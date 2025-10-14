# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import case, cast, func, not_
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base
from xivo_dao.helpers.exception import InputError

from .rightcallexten import RightCallExten


class RightCall(Base):
    __tablename__ = 'rightcall'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name', 'tenant_uuid'),
        Index('rightcall__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128), nullable=False, server_default='')
    passwd = Column(String(40), nullable=False, server_default='')
    authorization = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)
    rightcallextens = relationship(RightCallExten, cascade="all, delete-orphan")

    rightcall_members = relationship(
        'RightCallMember',
        primaryjoin='RightCallMember.rightcallid == RightCall.id',
        foreign_keys='RightCallMember.rightcallid',
        cascade='all, delete-orphan',
        back_populates='rightcall',
    )

    rightcall_outcalls = relationship(
        'RightCallMember',
        primaryjoin="""and_(
            RightCallMember.rightcallid == RightCall.id,
            RightCallMember.type == 'outcall'
        )""",
        foreign_keys='RightCallMember.rightcallid',
        viewonly=True,
    )
    outcalls = association_proxy('rightcall_outcalls', 'outcall')

    rightcall_groups = relationship(
        'RightCallMember',
        primaryjoin="""and_(
            RightCallMember.rightcallid == RightCall.id,
            RightCallMember.type == 'group'
        )""",
        foreign_keys='RightCallMember.rightcallid',
        viewonly=True,
    )
    groups = association_proxy('rightcall_groups', 'group')

    rightcall_users = relationship(
        'RightCallMember',
        primaryjoin="""and_(
            RightCallMember.rightcallid == RightCall.id,
            RightCallMember.type == 'user'
        )""",
        foreign_keys='RightCallMember.rightcallid',
        viewonly=True,
    )
    users = association_proxy('rightcall_users', 'user')

    @hybrid_property
    def password(self):
        if self.passwd == '':
            return None
        return self.passwd

    @password.expression
    def password(cls):
        return func.nullif(cls.passwd, '')

    @password.setter
    def password(self, value):
        if value is None:
            self.passwd = ''
        else:
            self.passwd = value

    @hybrid_property
    def mode(self):
        if self.authorization == 1:
            return 'allow'
        else:
            return 'deny'

    @mode.expression
    def mode(cls):
        return case((cls.authorization == 1, 'allow'), else_='deny')

    @mode.setter
    def mode(self, value):
        if value == 'allow':
            self.authorization = 1
        elif value == 'deny':
            self.authorization = 0
        else:
            raise InputError(
                f"cannot set mode to {value}. Only 'allow' or 'deny' are authorized"
            )

    @hybrid_property
    def enabled(self):
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)

    @property
    def extensions(self):
        return [rightcallexten.exten for rightcallexten in self.rightcallextens]

    @extensions.setter
    def extensions(self, values):
        old_rightcallextens = {
            rightcallexten.exten: rightcallexten
            for rightcallexten in self.rightcallextens
        }
        self.rightcallextens = []
        for value in set(values):
            if value in old_rightcallextens:
                self.rightcallextens.append(old_rightcallextens[value])
            else:
                self.rightcallextens.append(
                    RightCallExten(rightcallid=self.id, exten=value)
                )
