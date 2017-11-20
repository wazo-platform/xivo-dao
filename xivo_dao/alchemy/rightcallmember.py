# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import case, cast
from sqlalchemy.types import Integer, String, Enum

from xivo_dao.helpers.db_manager import Base


class RightCallMember(Base):

    __tablename__ = 'rightcallmember'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('rightcallid', 'type', 'typeval'),
    )

    id = Column(Integer, nullable=False)
    rightcallid = Column(Integer, nullable=False, server_default='0')
    type = Column(Enum('user', 'group', 'incall', 'outcall',
                       name='rightcallmember_type',
                       metadata=Base.metadata),
                  nullable=False)
    typeval = Column(String(128), nullable=False, server_default='0')

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
        return case([(cls.type == 'user', cast(cls.typeval, Integer))], else_=None)

    @user_id.setter
    def user_id(self, value):
        self.type = 'user'
        self.typeval = str(value)
