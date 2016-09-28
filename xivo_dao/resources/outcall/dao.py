# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from .persistor import OutcallPersistor
from .search import outcall_search

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return OutcallPersistor(session, outcall_search).search(parameters)


@daosession
def get(session, outcall_id):
    return OutcallPersistor(session, outcall_search).get_by({'id': outcall_id})


@daosession
def get_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).get_by(criteria)


@daosession
def find(session, outcall_id):
    return OutcallPersistor(session, outcall_search).find_by({'id': outcall_id})


@daosession
def find_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).find_all_by(criteria)


@daosession
def create(session, outcall):
    return OutcallPersistor(session, outcall_search).create(outcall)


@daosession
def edit(session, outcall):
    OutcallPersistor(session, outcall_search).edit(outcall)


@daosession
def delete(session, outcall):
    OutcallPersistor(session, outcall_search).delete(outcall)


# TODO: DELETE
@daosession
def exists(session, outcall_id):
    query = (session.query(Outcall)
             .filter(Outcall.id == outcall_id)
             )

    return query.count() > 0
