# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import String

from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.switchboard_member_user import SwitchboardMemberUser
from xivo_dao.helpers.uuid import new_uuid


class Switchboard(Base):

    __tablename__ = 'switchboard'
    __table_args__ = (
        PrimaryKeyConstraint('uuid'),
    )

    uuid = Column(String(38), nullable=False, default=new_uuid)
    name = Column(String(128), nullable=False)

    incall_dialactions = relationship('Dialaction',
                                      primaryjoin="""and_(Dialaction.category == 'incall',
                                                          Dialaction.action == 'switchboard',
                                                          Dialaction.actionarg1 == Switchboard.uuid)""",
                                      foreign_keys='Dialaction.actionarg1',
                                      viewonly=True)

    incalls = association_proxy('incall_dialactions', 'incall')

    switchboard_member_users = relationship('SwitchboardMemberUser',
                                            primaryjoin="""SwitchboardMemberUser.switchboard_uuid == Switchboard.uuid""",
                                            cascade='all, delete-orphan')

    user_members = association_proxy('switchboard_member_users', 'user',
                                     creator=lambda _user: SwitchboardMemberUser(user=_user))
