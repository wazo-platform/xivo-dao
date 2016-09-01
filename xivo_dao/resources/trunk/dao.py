# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.trunk.persistor import TrunkPersistor
from xivo_dao.resources.trunk.search import trunk_search


@daosession
def search(session, **parameters):
    return TrunkPersistor(session, trunk_search).search(parameters)


@daosession
def get(session, trunk_id):
    return TrunkPersistor(session, trunk_search).get_by({'id': trunk_id})


@daosession
def get_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).get_by(criteria)


@daosession
def find(session, trunk_id):
    return TrunkPersistor(session, trunk_search).find_by({'id': trunk_id})


@daosession
def find_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).find_all_by(criteria)


@daosession
def create(session, trunk):
    return TrunkPersistor(session, trunk_search).create(trunk)


@daosession
def edit(session, trunk):
    with flush_session(session):  # Maybe useless
        TrunkPersistor(session, trunk_search).edit(trunk)
        session.expire(trunk)
        TrunkFixes(session).fix(trunk.id)


@daosession
def delete(session, trunk):
    TrunkPersistor(session, trunk_search).delete(trunk)
