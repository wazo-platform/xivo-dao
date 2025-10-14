# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.sql import cast, select
from sqlalchemy.types import Boolean, Integer, String, Text

from xivo_dao.helpers.db_manager import Base

from .callerid import Callerid
from .extension import Extension
from .queue import Queue
from .rightcallmember import RightCallMember
from .schedulepath import SchedulePath


class GroupFeatures(Base):
    __tablename__ = 'groupfeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        Index('groupfeatures__idx__name', 'name'),
        Index('groupfeatures__idx__uuid', 'uuid'),
        Index('groupfeatures__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    uuid = Column(
        UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), nullable=False
    )
    tenant_uuid = Column(
        String(36), ForeignKey('tenant.uuid', ondelete='CASCADE'), nullable=False
    )
    name = Column(String(128), nullable=False)
    dtmf_record_toggle = Column(Boolean, nullable=False, server_default='false')
    label = Column(Text, nullable=False)
    transfer_user = Column(Integer, nullable=False, server_default='0')
    transfer_call = Column(Integer, nullable=False, server_default='0')
    write_caller = Column(Integer, nullable=False, server_default='0')
    write_calling = Column(Integer, nullable=False, server_default='0')
    ignore_forward = Column(Integer, nullable=False, server_default='0')
    timeout = Column(Integer)
    preprocess_subroutine = Column(String(79))
    mark_answered_elsewhere = Column(Integer, nullable=False, server_default='0')

    caller_id = relationship(
        'Callerid',
        primaryjoin="""and_(Callerid.type == 'group',
                            Callerid.typeval == GroupFeatures.id)""",
        foreign_keys='Callerid.typeval',
        cascade='all, delete-orphan',
        uselist=False,
        overlaps='caller_id',
    )

    caller_id_mode = association_proxy(
        'caller_id', 'mode', creator=lambda _mode: Callerid(type='group', mode=_mode)
    )
    caller_id_name = association_proxy(
        'caller_id', 'name', creator=lambda _name: Callerid(type='group', name=_name)
    )

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'group',
                            Extension.typeval == cast(GroupFeatures.id, String))""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    incall_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.category == 'incall',
                            Dialaction.action == 'group',
                            Dialaction.actionarg1 == cast(GroupFeatures.id, String))""",
        foreign_keys='Dialaction.actionarg1',
        viewonly=True,
    )

    incalls = association_proxy('incall_dialactions', 'incall')

    group_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.category == 'group',
                            Dialaction.categoryval == cast(GroupFeatures.id, String))""",
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('event'),
        foreign_keys='Dialaction.categoryval',
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'dialactions,'
            'ivr_choice",'
            'queue_dialactions,'
            'switchboard_dialactions,'
            'user_dialactions,'
        ),
    )

    user_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'group',
                            not_(QueueMember.interface.startswith('Local/')),
                            QueueMember.queue_name == GroupFeatures.name)""",
        order_by='QueueMember.position',
        foreign_keys='QueueMember.queue_name',
        cascade='all, delete-orphan',
        passive_updates=False,
        overlaps=(
            'agent_queue_members,'
            'extension_queue_members,'
            'user_queue_members,'
        ),  # fmt: skip
    )
    users = association_proxy('user_queue_members', 'user')

    extension_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'group',
                            QueueMember.interface.startswith('Local/'),
                            QueueMember.queue_name == GroupFeatures.name)""",
        order_by='QueueMember.position',
        foreign_keys='QueueMember.queue_name',
        cascade='all, delete-orphan',
        passive_updates=False,
        overlaps=(
            'agent_queue_members,'
            'user_queue_members,'
        ),  # fmt: skip
    )

    _queue = relationship(
        'Queue',
        primaryjoin="""and_(Queue.category == 'group',
                            Queue.name == GroupFeatures.name)""",
        foreign_keys='Queue.name',
        cascade='all, delete-orphan',
        uselist=False,
        passive_updates=False,
        overlaps='_queue',
    )

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.action == 'group',
                            Dialaction.actionarg1 == cast(GroupFeatures.id, String))""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
        overlaps='_dialaction_actions',
    )

    enabled = association_proxy('_queue', 'enabled')
    music_on_hold = association_proxy('_queue', 'musicclass')
    retry_delay = association_proxy('_queue', 'retry')
    ring_in_use = association_proxy('_queue', 'ring_in_use')
    ring_strategy = association_proxy('_queue', 'strategy')
    user_timeout = association_proxy('_queue', 'timeout')
    max_calls = association_proxy('_queue', 'maxlen')

    func_keys_group = relationship(
        'FuncKeyDestGroup',
        cascade='all, delete-orphan',
    )

    func_keys_group_member = relationship(
        'FuncKeyDestGroupMember',
        cascade='all, delete-orphan',
    )

    schedule_paths = relationship(
        'SchedulePath',
        primaryjoin="""and_(SchedulePath.path == 'group',
                            SchedulePath.pathid == GroupFeatures.id)""",
        foreign_keys='SchedulePath.pathid',
        cascade='all, delete-orphan',
        overlaps='schedule_paths',
    )

    schedules = association_proxy(
        'schedule_paths',
        'schedule',
        creator=lambda _schedule: SchedulePath(
            path='group', schedule_id=_schedule.id, schedule=_schedule
        ),
    )
    rightcall_members = relationship(
        'RightCallMember',
        primaryjoin="""and_(RightCallMember.type == 'group',
        RightCallMember.typeval == cast(GroupFeatures.id, String))""",
        foreign_keys='RightCallMember.typeval',
        cascade='all, delete-orphan',
        overlaps='rightcall_members',
    )
    call_permissions = association_proxy(
        'rightcall_members',
        'rightcall',
        creator=lambda _call_permission: RightCallMember(
            type='group', typeval=str(_call_permission.id), rightcall=_call_permission
        ),
    )

    call_pickup_interceptors = relationship(
        'PickupMember',
        primaryjoin="""and_(PickupMember.category == 'member',
                            PickupMember.membertype == 'group',
                            PickupMember.memberid == GroupFeatures.id)""",
        foreign_keys='PickupMember.memberid',
        cascade='delete, delete-orphan',
        overlaps='call_pickup_targets,call_pickup_interceptors,user,group',
    )

    call_pickup_targets = relationship(
        'PickupMember',
        primaryjoin="""and_(PickupMember.category == 'pickup',
                            PickupMember.membertype == 'group',
                            PickupMember.memberid == GroupFeatures.id)""",
        foreign_keys='PickupMember.memberid',
        cascade='delete, delete-orphan',
        overlaps='call_pickup_targets,call_pickup_interceptors,user,group',
    )

    call_pickup_interceptor_pickups = relationship(
        'Pickup',
        primaryjoin="""and_(
            PickupMember.category == 'member',
            PickupMember.membertype == 'group',
            PickupMember.memberid == GroupFeatures.id
        )""",
        secondary="join(PickupMember, Pickup, Pickup.id == PickupMember.pickupid)",
        secondaryjoin="Pickup.id == PickupMember.pickupid",
        foreign_keys='PickupMember.pickupid,PickupMember.memberid',
        viewonly=True,
    )
    users_from_call_pickup_user_targets = association_proxy(
        'call_pickup_interceptor_pickups',
        'user_targets',
    )
    users_from_call_pickup_group_targets = association_proxy(
        'call_pickup_interceptor_pickups',
        'users_from_group_targets',
    )

    def __init__(self, **kwargs):
        retry = kwargs.pop('retry_delay', 5)
        ring_in_use = kwargs.pop('ring_in_use', True)
        strategy = kwargs.pop('ring_strategy', 'ringall')
        timeout = kwargs.pop('user_timeout', 15)
        musicclass = kwargs.pop('music_on_hold', None)
        enabled = kwargs.pop('enabled', True)
        max_calls = kwargs.pop('max_calls', 0)
        super().__init__(**kwargs)
        if not self._queue:
            self._queue = Queue(
                retry=retry,
                ring_in_use=ring_in_use,
                strategy=strategy,
                timeout=timeout,
                musicclass=musicclass,
                enabled=enabled,
                queue_youarenext='queue-youarenext',
                queue_thereare='queue-thereare',
                queue_callswaiting='queue-callswaiting',
                queue_holdtime='queue-holdtime',
                queue_minutes='queue-minutes',
                queue_seconds='queue-seconds',
                queue_thankyou='queue-thankyou',
                queue_reporthold='queue-reporthold',
                periodic_announce='queue-periodic-announce',
                announce_frequency=0,
                periodic_announce_frequency=0,
                announce_round_seconds=0,
                announce_holdtime='no',
                wrapuptime=0,
                maxlen=max_calls,
                memberdelay=0,
                weight=0,
                category='group',
                autofill=1,
                announce_position='no',
            )

    @property
    def fallbacks(self):
        return self.group_dialactions

    # Note: fallbacks[key] = Dialaction() doesn't pass in this method
    @fallbacks.setter
    def fallbacks(self, dialactions):
        for event in list(self.group_dialactions.keys()):
            if event not in dialactions:
                self.group_dialactions.pop(event, None)

        for event, dialaction in dialactions.items():
            if dialaction is None:
                self.group_dialactions.pop(event, None)
                continue

            if event not in self.group_dialactions:
                dialaction.category = 'group'
                dialaction.event = event
                self.group_dialactions[event] = dialaction

            self.group_dialactions[event].action = dialaction.action
            self.group_dialactions[event].actionarg1 = dialaction.actionarg1
            self.group_dialactions[event].actionarg2 = dialaction.actionarg2

    @hybrid_property
    def mark_answered_elsewhere_bool(self):
        return self.mark_answered_elsewhere == 1

    @mark_answered_elsewhere_bool.setter
    def mark_answered_elsewhere_bool(self, value):
        self.mark_answered_elsewhere = int(value is True)

    @hybrid_property
    def exten(self):
        for extension in self.extensions:
            return extension.exten
        return None

    @exten.expression
    def exten(cls):
        return (
            select(Extension.exten)
            .where(Extension.type == 'group')
            .where(Extension.typeval == cast(cls.id, String))
            .scalar_subquery()
        )
