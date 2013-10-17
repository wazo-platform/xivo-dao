# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers.db_manager import Base, Type
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Enum, Text


class Queue(Base):

    __tablename__ = 'queue'

    name = Column(String(128), primary_key=True)
    musicclass = Column(String(128))
    announce = Column(String(128))
    context = Column(String(39))
    timeout = Column(Integer, default=0)
    monitor_type = Column('monitor-type', Enum('no', 'mixmonitor', name='queue_monitor_type', metadata=Type.metadata)),
    monitor_format = Column('monitor-format', String(128))
    queue_youarenext = Column(' queue-youarenext', String(128))
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
    announce_round_seconds = Column('announce-frequency', Integer)
    announce_holdtime = Column('announce-holdtime', String(4))
    retry = Column(Integer)
    wrapuptime = Column(Integer)
    maxlen = Column(Integer)
    servicelevel = Column(Integer)
    strategy = Column(String(11))
    joinempty = Column(String(255))
    leavewhenempty = Column(String(255))
    eventmemberstatus = Column(Integer, nullable=False, default=0)
    eventwhencalled = Column(Integer, nullable=False, default=0)
    ringinuse = Column(Integer, nullable=False, default=0)
    reportholdtime = Column(Integer, nullable=False, default=0)
    memberdelay = Column(Integer)
    weight = Column(Integer)
    timeoutrestart = Column(Integer, nullable=False, default=0)
    commented = Column(Integer, nullable=False, default=0)
    category = Column(Enum('group', 'queue', name='queue_category', metadata=Type.metadata), nullable=False),
    timeoutpriority = Column(String(10), nullable=False, default='app')
    autofill = Column(Integer, nullable=False, default=1)
    autopause = Column(Integer, nullable=False, default=1)
    setinterfacevar = Column(Integer, nullable=False, default=0)
    setqueueentryvar = Column(Integer, nullable=False, default=0)
    setqueuevar = Column(Integer, nullable=False, default=0)
    membermacro = Column(String(1024))
    min_announce_frequency = Column('min-announce-frequency', Integer, nullable=False, default=60)
    random_periodic_announc = Column('random-periodic-announc', Integer, nullable=False, default=0)
    announce_position = Column('announce-position', String(1024), nullable=False, default='yes')
    announce_position_limit = Column('announce-position-limit', Integer, nullable=False, default=5)
    defaultrule = Column(String(1024))
