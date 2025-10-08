# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Index, PrimaryKeyConstraint
from sqlalchemy.sql.schema import CheckConstraint
from sqlalchemy.types import Enum, Integer, String, Text

from xivo_dao.helpers.asterisk import AsteriskOptionsMixin
from xivo_dao.helpers.db_manager import Base


class Queue(Base, AsteriskOptionsMixin):
    EXCLUDE_OPTIONS = {
        'name',
        'category',
        'commented',
    }
    EXCLUDE_OPTIONS_CONFD = {
        'musicclass',
    }
    AST_TRUE_INTEGER_COLUMNS = {
        'ringinuse',
        'timeoutrestart',
        'autofill',
        'setinterfacevar',
        'setqueueentryvar',
        'setqueuevar',
        'reportholdtime',
        'random-periodic-announce',
    }

    # This should eventually be a column to set arbitrary asterisk options
    _options = []

    __tablename__ = 'queue'
    __table_args__ = (
        PrimaryKeyConstraint('name'),
        Index('queue__idx__category', 'category'),
        CheckConstraint("autopause in ('no', 'yes', 'all')"),
    )

    name = Column(String(128))
    musicclass = Column(String(128))
    announce = Column(String(128))
    context = Column(String(79))
    timeout = Column(Integer, server_default='0')
    monitor_type = Column(
        'monitor-type',
        Enum('no', 'mixmonitor', name='queue_monitor_type', metadata=Base.metadata),
    )
    monitor_format = Column('monitor-format', String(128))
    queue_youarenext = Column('queue-youarenext', String(128))
    queue_thereare = Column('queue-thereare', String(128))
    queue_callswaiting = Column('queue-callswaiting', String(128))
    queue_holdtime = Column('queue-holdtime', String(128))
    queue_minutes = Column('queue-minutes', String(128))
    queue_seconds = Column('queue-seconds', String(128))
    queue_thankyou = Column('queue-thankyou', String(128))
    queue_reporthold = Column('queue-reporthold', String(128))
    periodic_announce = Column('periodic-announce', Text)
    announce_frequency = Column('announce-frequency', Integer)
    periodic_announce_frequency = Column('periodic-announce-frequency', Integer)
    announce_round_seconds = Column('announce-round-seconds', Integer)
    announce_holdtime = Column('announce-holdtime', String(4))
    retry = Column(Integer)
    wrapuptime = Column(Integer)
    maxlen = Column(Integer)
    servicelevel = Column(Integer)
    strategy = Column(String(11))
    joinempty = Column(String(255))
    leavewhenempty = Column(String(255))
    ringinuse = Column(Integer, nullable=False, server_default='0')
    reportholdtime = Column(Integer, nullable=False, server_default='0')
    memberdelay = Column(Integer)
    weight = Column(Integer)
    timeoutrestart = Column(Integer, nullable=False, server_default='0')
    commented = Column(Integer, nullable=False, server_default='0')
    category = Column(
        Enum('group', 'queue', name='queue_category', metadata=Base.metadata),
        nullable=False,
    )
    timeoutpriority = Column(String(10), nullable=False, server_default='app')
    autofill = Column(Integer, nullable=False, server_default='1')
    autopause = Column(String(3), nullable=False, server_default='no')
    setinterfacevar = Column(Integer, nullable=False, server_default='0')
    setqueueentryvar = Column(Integer, nullable=False, server_default='0')
    setqueuevar = Column(Integer, nullable=False, server_default='0')
    membermacro = Column(String(1024))
    min_announce_frequency = Column(
        'min-announce-frequency', Integer, nullable=False, server_default='60'
    )
    random_periodic_announce = Column(
        'random-periodic-announce', Integer, nullable=False, server_default='0'
    )
    announce_position = Column(
        'announce-position', String(1024), nullable=False, server_default='yes'
    )
    announce_position_limit = Column(
        'announce-position-limit', Integer, nullable=False, server_default='5'
    )
    defaultrule = Column(String(1024))

    groupfeatures = relationship(
        'GroupFeatures',
        primaryjoin="""and_(Queue.category == 'group',
                            Queue.name == GroupFeatures.name)""",
        foreign_keys='Queue.name',
        uselist=False,
        viewonly=True,
    )

    queuefeatures = relationship(
        'QueueFeatures',
        primaryjoin="""and_(Queue.category == 'queue',
                            Queue.name == QueueFeatures.name)""",
        foreign_keys='Queue.name',
        uselist=False,
        viewonly=True,
    )

    @hybrid_property
    def enabled(self):
        if self.commented is None:
            return None
        return self.commented == 0

    @enabled.setter
    def enabled(self, value):
        self.commented = int(value is False) if value is not None else None

    @hybrid_property
    def ring_in_use(self):
        return bool(self.ringinuse)

    @ring_in_use.setter
    def ring_in_use(self, value):
        self.ringinuse = int(value)

    @property
    def label(self):
        try:
            if self.category == 'group':
                return self.groupfeatures.label
            elif self.category == 'queue':
                return self.queuefeatures.displayname
        except AttributeError:
            pass
        return 'unknown'
