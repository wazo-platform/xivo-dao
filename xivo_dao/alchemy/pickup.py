# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import Base

from .pickupmember import PickupMember


class Pickup(Base):

    __tablename__ = 'pickup'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        ForeignKeyConstraint(('entity_id',),
                             ('entity.id',),
                             ondelete='RESTRICT'),
        UniqueConstraint('name')
    )

    id = Column(Integer, nullable=False, autoincrement=False)
    entity_id = Column(Integer)
    name = Column(String(128), nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    entity = relationship(Entity)

    targets = relationship(
        'PickupMember',
        primaryjoin="""and_(PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'member')""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan'
    )
    user_targets = association_proxy('targets', 'user',
                                     creator=lambda _user: PickupMember(user=_user,
                                                                        category='member',
                                                                        membertype='user'))
    group_targets = association_proxy('targets', 'group',
                                      creator=lambda _group: PickupMember(group=_group,
                                                                          category='member',
                                                                          membertype='group'))

    interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'pickup')""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan'
    )
    user_interceptors = association_proxy('interceptors', 'user',
                                          creator=lambda _user: PickupMember(user=_user,
                                                                             category='pickup',
                                                                             membertype='user'))
    group_interceptors = association_proxy('interceptors', 'group',
                                           creator=lambda _group: PickupMember(group=_group,
                                                                               category='pickup',
                                                                               membertype='group'))

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.expression
    def enabled(cls):
        return not_(cast(cls.commented, Boolean))

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False)
