# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from .persistor import SwitchboardPersistor
from .search import switchboard_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return SwitchboardPersistor(session, switchboard_search).search(parameters)


@daosession
def get(session, switchboard_id):
    return SwitchboardPersistor(session, switchboard_search).get_by({'id': str(switchboard_id)})


@daosession
def get_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).get_by(criteria)


@daosession
def find(session, switchboard_id):
    return SwitchboardPersistor(session, switchboard_search).find_by({'id': str(switchboard_id)})


@daosession
def find_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SwitchboardPersistor(session, switchboard_search).find_all_by(criteria)


@daosession
def create(session, switchboard):
    return SwitchboardPersistor(session, switchboard_search).create(switchboard)


@daosession
def edit(session, switchboard):
    return SwitchboardPersistor(session, switchboard_search).edit(switchboard)


@daosession
def delete(session, switchboard):
    SwitchboardPersistor(session, switchboard_search).delete(switchboard)
