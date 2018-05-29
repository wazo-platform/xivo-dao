# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.schema import (
    Column,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.types import Integer, String

from xivo_dao.helpers.db_manager import Base

from .queue import Queue

DEFAULT_QUEUE_OPTIONS = {
    'timeout': '15',
    'queue-youarenext': 'queue-youarenext',
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
    )

    id = Column(Integer)
    name = Column(String(128), nullable=False)
    displayname = Column(String(128), nullable=False)
    number = Column(String(40), nullable=False, server_default='')
    context = Column(String(39))
    data_quality = Column(Integer, nullable=False, server_default='0')
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
    preprocess_subroutine = Column(String(39))
    announce_holdtime = Column(Integer, nullable=False, server_default='0')
    waittime = Column(Integer)
    waitratio = Column(DOUBLE_PRECISION)

    _queue = relationship(
        'Queue',
        primaryjoin="""and_(Queue.category == 'queue',
                            Queue.name == QueueFeatures.name)""",
        foreign_keys='Queue.name',
        cascade='all, delete-orphan',
        uselist=False,
        passive_updates=False,
    )
    enabled = association_proxy('_queue', 'enabled')
    options = association_proxy('_queue', 'options')

    extensions = relationship(
        'Extension',
        primaryjoin="""and_(Extension.type == 'queue',
                            Extension.typeval == cast(QueueFeatures.id, String))""",
        foreign_keys='Extension.typeval',
        viewonly=True,
    )

    func_keys = relationship(
        'FuncKeyDestQueue',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        options = kwargs.pop('options', [])
        options = self.merge_options_with_default_values(options)
        enabled = kwargs.pop('enabled', True)
        super(QueueFeatures, self).__init__(**kwargs)
        if not self._queue:
            self._queue = Queue(
                # 'name' is set by the relationship foreign_key
                category='queue',
                enabled=enabled,
                options=options,
            )

    def merge_options_with_default_values(self, options):
        result = dict(DEFAULT_QUEUE_OPTIONS)
        for option in options:
            result[option[0]] = option[1]
        return [[key, value] for key, value in result.items()]
