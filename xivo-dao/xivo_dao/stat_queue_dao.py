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

from sqlalchemy import distinct
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_manager import daosession


@daosession
def _get(session, queue_id):
    return session.query(StatQueue).filter(StatQueue.id == queue_id)[0]


@daosession
def id_from_name(session, queue_name):
    res = session.query(StatQueue).filter(StatQueue.name == queue_name)
    if res.count() == 0:
        raise LookupError('No such queue')
    return res[0].id


def insert_if_missing(session, all_queues):
    all_queues = set(all_queues)
    old_queues = set(r[0] for r in session.query(distinct(StatQueue.name)))

    missing_queues = list(all_queues - old_queues)

    for queue_name in missing_queues:
        new_queue = StatQueue()
        new_queue.name = queue_name
        session.add(new_queue)


def clean_table(session):
    session.query(StatQueue).delete()
