# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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


from xivo_dao.resources.incall.persistor import IncallPersistor
from xivo_dao.resources.incall.search import incall_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return IncallPersistor(session, incall_search).search(parameters)


@daosession
def get(session, incall_id):
    return IncallPersistor(session, incall_search).get_by({'id': incall_id})


@daosession
def get_by(session, **criteria):
    return IncallPersistor(session, incall_search).get_by(criteria)


@daosession
def find(session, incall_id):
    return IncallPersistor(session, incall_search).find_by({'id': incall_id})


@daosession
def find_by(session, **criteria):
    return IncallPersistor(session, incall_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IncallPersistor(session, incall_search).find_all_by(criteria)


@daosession
def create(session, incall):
    return IncallPersistor(session, incall_search).create(incall)


@daosession
def edit(session, incall):
    IncallPersistor(session, incall_search).edit(incall)


@daosession
def delete(session, incall):
    IncallPersistor(session, incall_search).delete(incall)
