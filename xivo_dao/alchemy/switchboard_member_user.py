# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base


class SwitchboardMemberUser(Base):

    __tablename__ = 'switchboard_member_user'
    __table_args__ = (
        PrimaryKeyConstraint('switchboard_uuid', 'user_uuid'),
        Index('switchboard_member_user__idx__switchboard_uuid', 'switchboard_uuid'),
    )

    switchboard_uuid = Column(String(38), ForeignKey('switchboard.uuid'), nullable=False)
    user_uuid = Column(String(38), ForeignKey('userfeatures.uuid'), nullable=False)

    switchboard = relationship('Switchboard')
    user = relationship('UserFeatures')
