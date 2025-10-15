# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    CheckConstraint,
    Column,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import case, cast
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class RightCallMember(Base):
    __tablename__ = 'rightcallmember'

    id = Column(Integer, nullable=False)
    rightcallid = Column(Integer, nullable=False, server_default='0')
    type = Column(String(64), nullable=False)
    typeval = Column(String(128), nullable=False, server_default='0')

    group = relationship(
        'GroupFeatures',
        primaryjoin="""and_(RightCallMember.type == 'group',
                            RightCallMember.typeval == cast(GroupFeatures.id, String))""",
        foreign_keys='RightCallMember.typeval',
        viewonly=True,
    )

    outcall = relationship(
        'Outcall',
        primaryjoin="""and_(RightCallMember.type == 'outcall',
                            RightCallMember.typeval == cast(Outcall.id, String))""",
        foreign_keys='RightCallMember.typeval',
        viewonly=True,
    )

    user = relationship(
        'UserFeatures',
        primaryjoin="""and_(RightCallMember.type == 'user',
                            RightCallMember.typeval == cast(UserFeatures.id, String))""",
        foreign_keys='RightCallMember.typeval',
        viewonly=True,
    )

    rightcall = relationship(
        'RightCall',
        primaryjoin='RightCall.id == RightCallMember.rightcallid',
        foreign_keys='RightCallMember.rightcallid',
        back_populates='rightcall_members',
    )

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('rightcallid', 'type', 'typeval'),
        CheckConstraint(
            type.in_(['group', 'outcall', 'user']), name='rightcallmember_type_check'
        ),
    )

    @hybrid_property
    def call_permission_id(self):
        return self.rightcallid

    @call_permission_id.setter
    def call_permission_id(self, value):
        self.rightcallid = value

    @hybrid_property
    def user_id(self):
        if self.type == 'user':
            return int(self.typeval)
        return None

    @user_id.expression
    def user_id(cls):
        return case((cls.type == 'user', cast(cls.typeval, Integer)), else_=None)

    @user_id.setter
    def user_id(self, value):
        self.type = 'user'
        self.typeval = str(value)
