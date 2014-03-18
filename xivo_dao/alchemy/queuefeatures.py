# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.schema import Column, ForeignKeyConstraint
from sqlalchemy.types import Integer, String
from xivo_dao.helpers.db_manager import Base
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from xivo_dao.alchemy.queue import Queue

test_dependencies = [Queue]


class QueueFeatures(Base):

    __tablename__ = 'queuefeatures'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    displayname = Column(String(128), nullable=False)
    number = Column(String(40), nullable=False, default='')
    context = Column(String(39))
    data_quality = Column(Integer, nullable=False, default=0)
    hitting_callee = Column(Integer, nullable=False, default=0)
    hitting_caller = Column(Integer, nullable=False, default=0)
    retries = Column(Integer, nullable=False, default=0)
    ring = Column(Integer, nullable=False, default=0)
    transfer_user = Column(Integer, nullable=False, default=0)
    transfer_call = Column(Integer, nullable=False, default=0)
    write_caller = Column(Integer, nullable=False, default=0)
    write_calling = Column(Integer, nullable=False, default=0)
    url = Column(String(255), nullable=False, default='')
    announceoverride = Column(String(128), nullable=False, default='')
    timeout = Column(Integer, nullable=False, default=0)
    preprocess_subroutine = Column(String(39))
    announce_holdtime = Column(Integer, nullable=False, default=0)
    waittime = Column(Integer)
    waitratio = Column(DOUBLE_PRECISION)

ForeignKeyConstraint(columns=[QueueFeatures.id], refcolumns=[StatCallOnQueue.queue_id], ondelete="CASCADE")
ForeignKeyConstraint(columns=[QueueFeatures.id], refcolumns=[StatQueuePeriodic.queue_id], ondelete="CASCADE")
ForeignKeyConstraint(columns=[QueueFeatures.id], refcolumns=[RecordCampaigns.queue_id], ondelete="CASCADE")
