# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.alchemy.stat_queue_periodic import StatQueuePeriodic
from sqlalchemy.sql.functions import max


def insert_stats(session, stats, period_start):
    for queue_id, queue_stats in stats.iteritems():
        entry = StatQueuePeriodic()
        entry.time = period_start
        entry.abandoned = queue_stats.get('abandoned', 0)
        entry.answered = queue_stats.get('answered', 0)
        entry.full = queue_stats.get('full', 0)
        entry.joinempty = queue_stats.get('joinempty', 0)
        entry.leaveempty = queue_stats.get('leaveempty', 0)
        entry.closed = queue_stats.get('closed', 0)
        entry.timeout = queue_stats.get('timeout', 0)
        entry.divert_ca_ratio = queue_stats.get('divert_ca_ratio', 0)
        entry.divert_waittime = queue_stats.get('divert_waittime', 0)
        entry.total = queue_stats['total']
        entry.queue_id = queue_id

        session.add(entry)


def get_most_recent_time(session):
    res = session.query(max(StatQueuePeriodic.time)).first()[0]
    if res is None:
        raise LookupError('Table is empty')
    return res


def clean_table(session):
    session.query(StatQueuePeriodic).delete()


def remove_after(session, date):
    session.query(StatQueuePeriodic).filter(StatQueuePeriodic.time >= date).delete()
