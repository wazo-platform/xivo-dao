# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall SAS. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queuefeatures import QueueFeatures

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def all_queues():
    return _session().query(QueueFeatures).all()


def _get(queue_id):
    return _session().query(QueueFeatures).filter(QueueFeatures.id == queue_id)[0]


def id_from_name(queue_name):
    result = _session().query(QueueFeatures.id).filter(QueueFeatures.name == queue_name).first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result.id


def queue_name(queue_id):
    result = _session().query(QueueFeatures.name).filter(QueueFeatures.id == queue_id).first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result.name


def is_a_queue(name):
    try:
        id_from_name(name)
    except LookupError:
        return False
    else:
        return True


def is_user_member_of_queue(user_id, queue_id):
    statement = '''\
SELECT
    1 AS found
FROM
    queuefeatures
JOIN
    queuemember on queuemember.queue_name = queuefeatures.name
WHERE
    queuefeatures.id = :queue_id AND
    (queuemember.usertype = 'user' AND queuemember.userid = :user_id OR
     queuemember.usertype = 'agent' AND queuemember.userid = (
         SELECT
             agentid
         FROM
             userfeatures
         WHERE
             id = :user_id
        )
    )
'''
    row = (_session()
           .query('found')
           .from_statement(statement)
           .params(user_id=user_id, queue_id=queue_id)
           .first())
    return row is not None


def get_queue_name(queue_id):
    return _get(queue_id).name


def get_display_name_number(queue_id):
    queue = _get(queue_id)
    return queue.displayname, queue.number


def add_queue(queue):
    if type(queue) != QueueFeatures:
        raise ValueError('Wrong object passed')

    _session().add(queue)
    _session().commit()
