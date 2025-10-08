# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.sql import cast, not_
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .pickupmember import PickupMember


class Pickup(Base):
    __tablename__ = 'pickup'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('pickup__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer, nullable=False, autoincrement=False)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128), nullable=False)
    commented = Column(Integer, nullable=False, server_default='0')
    description = Column(Text)

    pickupmember_user_targets = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'pickup',
            PickupMember.membertype == 'user'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_interceptors,'
            'pickupmember_group_targets,'
            'pickupmember_queue_interceptors,'
            'pickupmember_queue_targets,'
            'pickupmember_user_interceptors,'
        ),
    )
    user_targets = association_proxy(
        'pickupmember_user_targets',
        'user',
        creator=lambda _user: PickupMember(
            user=_user, category='pickup', membertype='user'
        ),
    )

    pickupmember_group_targets = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'pickup',
            PickupMember.membertype == 'group'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_interceptors,'
            'pickupmember_queue_interceptors,'
            'pickupmember_queue_targets,'
            'pickupmember_user_interceptors,'
            'pickupmember_user_targets,'
        ),
    )
    group_targets = association_proxy(
        'pickupmember_group_targets',
        'group',
        creator=lambda _group: PickupMember(
            group=_group, category='pickup', membertype='group'
        ),
    )
    users_from_group_targets = association_proxy(
        'pickupmember_group_targets', 'users_from_group'
    )

    pickupmember_user_interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'member',
            PickupMember.membertype == 'user'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_interceptors,'
            'pickupmember_group_targets,'
            'pickupmember_queue_interceptors,'
            'pickupmember_queue_targets,'
            'pickupmember_user_targets,'
        ),
    )
    user_interceptors = association_proxy(
        'pickupmember_user_interceptors',
        'user',
        creator=lambda _user: PickupMember(
            user=_user, category='member', membertype='user'
        ),
    )

    pickupmember_group_interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'member',
            PickupMember.membertype == 'group'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_targets,'
            'pickupmember_queue_interceptors,'
            'pickupmember_queue_targets,'
            'pickupmember_user_interceptors,'
            'pickupmember_user_targets,'
        ),
    )
    group_interceptors = association_proxy(
        'pickupmember_group_interceptors',
        'group',
        creator=lambda _group: PickupMember(
            group=_group, category='member', membertype='group'
        ),
    )

    pickupmember_queue_targets = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'pickup',
            PickupMember.membertype == 'queue'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_interceptors,'
            'pickupmember_group_targets,'
            'pickupmember_queue_interceptors,'
            'pickupmember_user_interceptors,'
            'pickupmember_user_targets,'
        ),
    )

    pickupmember_queue_interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(
            PickupMember.pickupid == Pickup.id,
            PickupMember.category == 'member',
            PickupMember.membertype == 'queue'
        )""",
        foreign_keys='PickupMember.pickupid',
        cascade='all, delete-orphan',
        overlaps=(
            'pickupmember_group_interceptors,'
            'pickupmember_group_targets,'
            'pickupmember_queue_targets,'
            'pickupmember_user_interceptors,'
            'pickupmember_user_targets,'
        ),
    )

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
