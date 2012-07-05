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

from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.alchemy import dbconnection

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get(queue_id):
    return _session().query(QueueFeatures).filter(QueueFeatures.id == queue_id)[0]


def id_from_name(queue_name):
    res = _session().query(QueueFeatures).filter(QueueFeatures.name == queue_name)
    if res.count() == 0:
        raise LookupError('No such queue')
    return res[0].id


def queue_name(queue_id):
    res = _session().query(QueueFeatures).filter(QueueFeatures.id == queue_id)
    if res.count() == 0:
        raise LookupError('No such queue')
    return res[0].name


def is_a_queue(self, name):
    try:
        self.id_from_name(name)
    except LookupError:
        return False
    else:
        return True


def get_queue_name(queue_id):
    return _get(queue_id).name


def get_display_name_number(queue_id):
    queue = _get(queue_id)
    return queue.displayname, queue.number
