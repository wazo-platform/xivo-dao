# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.schema import Column, PrimaryKeyConstraint
from sqlalchemy.types import Integer, Enum

from xivo_dao.helpers.db_manager import Base


class PickupMember(Base):
    __tablename__ = 'pickupmember'
    __table_args__ = (
        PrimaryKeyConstraint('pickupid', 'category', 'membertype', 'memberid'),
    )

    pickupid = Column(Integer, nullable=False, autoincrement=False)
    category = Column(Enum('member',
                           'pickup',
                           name='pickup_category',
                           metadata=Base.metadata), nullable=False, autoincrement=False)
    membertype = Column(Enum('group',
                             'queue',
                             'user',
                             name='pickup_membertype',
                             metadata=Base.metadata), nullable=False, autoincrement=False)
    memberid = Column(Integer, nullable=False, autoincrement=False)
