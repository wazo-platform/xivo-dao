# Copyright 2007-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import cast, func, select
from sqlalchemy.types import Boolean, Integer, String

from xivo_dao.helpers.db_manager import Base

from .callerid import Callerid
from .extension import Extension
from .queue import Queue
from .schedulepath import SchedulePath

DEFAULT_QUEUE_OPTIONS = {
    'timeout': '15',
    'queue-youarenext': 'queue-youarenext',
    'queue-thereare': 'queue-thereare',
    'queue-callswaiting': 'queue-callswaiting',
    'queue-holdtime': 'queue-holdtime',
    'queue-minutes': 'queue-minutes',
    'queue-seconds': 'queue-seconds',
    'queue-thankyou': 'queue-thankyou',
    'queue-reporthold': 'queue-reporthold',
    'periodic-announce': 'queue-periodic-announce',
    'announce-frequency': '0',
    'periodic-announce-frequency': '0',
    'announce-round-seconds': '0',
    'announce-holdtime': 'no',
    'retry': '5',
    'wrapuptime': '0',
    'maxlen': '0',
    'servicelevel': '0',
    'strategy': 'ringall',
    'memberdelay': '0',
    'weight': '0',
    'timeoutpriority': 'conf',
    'setqueueentryvar': '1',
    'setqueuevar': '1',
}


class QueueFeatures(Base):
    __tablename__ = 'queuefeatures'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('name'),
        Index('queuefeatures__idx__context', 'context'),
        Index('queuefeatures__idx__number', 'number'),
        Index('queuefeatures__idx__tenant_uuid', 'tenant_uuid'),
    )

    id = Column(Integer)
    tenant_uuid = Column(
        String(36),
        ForeignKey('tenant.uuid', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(128), nullable=False)
    displayname = Column(String(128), nullable=False)
    number = Column(String(40))
    context = Column(String(79))
    data_quality = Column(Integer, nullable=False, server_default='0')
    dtmf_record_toggle = Column(Boolean, nullable=False, server_default='false')
    hitting_callee = Column(Integer, nullable=False, server_default='0')
    hitting_caller = Column(Integer, nullable=False, server_default='0')
    retries = Column(Integer, nullable=False, server_default='0')
    ring = Column(Integer, nullable=False, server_default='0')
    transfer_user = Column(Integer, nullable=False, server_default='0')
    transfer_call = Column(Integer, nullable=False, server_default='0')
    write_caller = Column(Integer, nullable=False, server_default='0')
    write_calling = Column(Integer, nullable=False, server_default='0')
    ignore_forward = Column(Integer, nullable=False, server_default='1')
    url = Column(String(255), nullable=False, server_default='')
    announceoverride = Column(String(128), nullable=False, server_default='')
    timeout = Column(Integer)
    preprocess_subroutine = Column(String(79))
    announce_holdtime = Column(Integer, nullable=False, server_default='0')
    waittime = Column(Integer)
    waitratio = Column(DOUBLE_PRECISION)
    mark_answered_elsewhere = Column(Integer, nullable=False, server_default='1')

    _queue = relationship(
        'Queue',
        primaryjoin="""and_(Queue.category == 'queue',
                            Queue.name == QueueFeatures.name)""",
        foreign_keys='Queue.name',
        cascade='all, delete-orphan',
        uselist=False,
        passive_updates=False,
        overlaps='_queue',
    )
    enabled = association_proxy('_queue', 'enabled')
    options = association_proxy('_queue', 'options')
    music_on_hold = association_proxy('_queue', 'musicclass')

    caller_id = relationship(
        'Callerid',
        primaryjoin="""and_(Callerid.type == 'queue',
                            Callerid.typeval == QueueFeatures.id)""",
        foreign_keys='Callerid.typeval',
        cascade='all, delete-orphan',
        uselist=False,
        overlaps='caller_id',
    )

    caller_id_mode = association_proxy(
        'caller_id', 'mode', creator=lambda _mode: Callerid(type='queue', mode=_mode)
    )
    caller_id_name = association_proxy(
        'caller_id', 'name', creator=lambda _name: Callerid(type='queue', name=_name)
    )

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'queue',
                            Extension.typeval == cast(QueueFeatures.id, String))""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    func_keys = relationship('FuncKeyDestQueue', cascade='all, delete-orphan')

    queue_dialactions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.category == 'queue',
                            Dialaction.categoryval == cast(QueueFeatures.id, String))""",
        foreign_keys='Dialaction.categoryval',
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('event'),
        overlaps=(
            'callfilter_dialactions,'
            'dialaction,'
            'dialactions,'
            'group_dialactions,'
            'ivr_choice",'
            'switchboard_dialactions,'
            'user_dialactions,'
        ),
    )

    _dialaction_actions = relationship(
        'Dialaction',
        primaryjoin="""and_(Dialaction.action == 'queue',
                            Dialaction.actionarg1 == cast(QueueFeatures.id, String))""",
        foreign_keys='Dialaction.actionarg1',
        cascade='all, delete-orphan',
        overlaps='_dialaction_actions',
    )

    user_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'queue',
                            QueueMember.usertype == 'user',
                            QueueMember.queue_name == QueueFeatures.name)""",
        foreign_keys='QueueMember.queue_name',
        order_by='QueueMember.position',
        cascade='all, delete-orphan',
        overlaps=(
            'agent_queue_members,'
            'extension_queue_members,'
            'user_queue_members,'
        ),  # fmt: skip
    )

    agent_queue_members = relationship(
        'QueueMember',
        primaryjoin="""and_(QueueMember.category == 'queue',
                            QueueMember.usertype == 'agent',
                            QueueMember.queue_name == QueueFeatures.name)""",
        foreign_keys='QueueMember.queue_name',
        order_by='QueueMember.position',
        cascade='all, delete-orphan',
        overlaps=(
            'extension_queue_members,'
            'user_queue_members,'
        ),  # fmt: skip
    )

    schedule_paths = relationship(
        'SchedulePath',
        primaryjoin="""and_(SchedulePath.path == 'queue',
                            SchedulePath.pathid == QueueFeatures.id)""",
        foreign_keys='SchedulePath.pathid',
        cascade='all, delete-orphan',
        overlaps='schedule_paths',
    )
    schedules = association_proxy(
        'schedule_paths',
        'schedule',
        creator=lambda _schedule: SchedulePath(path='queue', schedule=_schedule),
    )

    def __init__(self, **kwargs):
        options = kwargs.pop('options', [])
        options = self.merge_options_with_default_values(options)
        enabled = kwargs.pop('enabled', True)
        music_on_hold = kwargs.pop('music_on_hold', None)
        super().__init__(**kwargs)
        if not self._queue:
            self._queue = Queue(
                # 'name' is set by the relationship foreign_key
                category='queue',
                enabled=enabled,
                musicclass=music_on_hold,
                options=options,
            )

    def merge_options_with_default_values(self, options):
        result = dict(DEFAULT_QUEUE_OPTIONS)
        for option in options:
            result[option[0]] = option[1]
        return [[key, value] for key, value in result.items()]

    @property
    def wait_time_destination(self):
        return self.queue_dialactions.get('qwaittime')

    @wait_time_destination.setter
    def wait_time_destination(self, destination):
        self._set_dialaction('qwaittime', destination)

    @property
    def wait_ratio_destination(self):
        return self.queue_dialactions.get('qwaitratio')

    @wait_ratio_destination.setter
    def wait_ratio_destination(self, destination):
        self._set_dialaction('qwaitratio', destination)

    @property
    def fallbacks(self):
        return self.queue_dialactions

    # Note: fallbacks[key] = Dialaction() doesn't pass in this method
    @fallbacks.setter
    def fallbacks(self, dialactions):
        for event in ('noanswer', 'busy', 'congestion', 'chanunavail'):
            if event not in dialactions:
                self.queue_dialactions.pop(event, None)

        for event, dialaction in dialactions.items():
            self._set_dialaction(event, dialaction)

    def _set_dialaction(self, event, dialaction):
        if dialaction is None:
            self.queue_dialactions.pop(event, None)
            return

        if event not in self.queue_dialactions:
            dialaction.event = event
            dialaction.category = 'queue'
            self.queue_dialactions[event] = dialaction

        self.queue_dialactions[event].action = dialaction.action
        self.queue_dialactions[event].actionarg1 = dialaction.actionarg1
        self.queue_dialactions[event].actionarg2 = dialaction.actionarg2

    def fix_extension(self):
        self.number = None
        self.context = None
        for extension in self.extensions:
            self.number = extension.exten
            self.context = extension.context
            return

    @hybrid_property
    def label(self):
        if self.displayname == '':
            return None
        return self.displayname

    @label.expression
    def label(cls):
        return func.nullif(cls.displayname, '')

    @label.setter
    def label(self, value):
        if value is None:
            self.displayname = ''
        else:
            self.displayname = value

    @hybrid_property
    def data_quality_bool(self):
        return self.data_quality == 1

    @data_quality_bool.setter
    def data_quality_bool(self, value):
        self.data_quality = int(value is True)

    @hybrid_property
    def ignore_forward_bool(self):
        return self.ignore_forward == 1

    @ignore_forward_bool.setter
    def ignore_forward_bool(self, value):
        self.ignore_forward = int(value is True)

    @hybrid_property
    def dtmf_hangup_callee_enabled(self):
        return self.hitting_callee == 1

    @dtmf_hangup_callee_enabled.setter
    def dtmf_hangup_callee_enabled(self, value):
        self.hitting_callee = int(value is True)

    @hybrid_property
    def dtmf_hangup_caller_enabled(self):
        return self.hitting_caller == 1

    @dtmf_hangup_caller_enabled.setter
    def dtmf_hangup_caller_enabled(self, value):
        self.hitting_caller = int(value is True)

    @hybrid_property
    def dtmf_transfer_callee_enabled(self):
        return self.transfer_user == 1

    @dtmf_transfer_callee_enabled.setter
    def dtmf_transfer_callee_enabled(self, value):
        self.transfer_user = int(value is True)

    @hybrid_property
    def dtmf_transfer_caller_enabled(self):
        return self.transfer_call == 1

    @dtmf_transfer_caller_enabled.setter
    def dtmf_transfer_caller_enabled(self, value):
        self.transfer_call = int(value is True)

    @hybrid_property
    def dtmf_record_callee_enabled(self):
        return self.write_caller == 1

    @dtmf_record_callee_enabled.setter
    def dtmf_record_callee_enabled(self, value):
        self.write_caller = int(value is True)

    @hybrid_property
    def dtmf_record_caller_enabled(self):
        return self.write_calling == 1

    @dtmf_record_caller_enabled.setter
    def dtmf_record_caller_enabled(self, value):
        self.write_calling = int(value is True)

    @hybrid_property
    def retry_on_timeout(self):
        return not self.retries == 1

    @retry_on_timeout.setter
    def retry_on_timeout(self, value):
        self.retries = int(value is False)

    @hybrid_property
    def ring_on_hold(self):
        return self.ring == 1

    @ring_on_hold.setter
    def ring_on_hold(self, value):
        self.ring = int(value is True)

    @hybrid_property
    def announce_hold_time_on_entry(self):
        return self.announce_holdtime == 1

    @announce_hold_time_on_entry.setter
    def announce_hold_time_on_entry(self, value):
        self.announce_holdtime = int(value is True)

    @hybrid_property
    def wait_time_threshold(self):
        return self.waittime

    @wait_time_threshold.setter
    def wait_time_threshold(self, value):
        self.waittime = value

    @hybrid_property
    def wait_ratio_threshold(self):
        return self.waitratio

    @wait_ratio_threshold.setter
    def wait_ratio_threshold(self, value):
        self.waitratio = value

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
            .where(Extension.type == 'queue')
            .where(Extension.typeval == cast(cls.id, String))
            .scalar_subquery()
        )
