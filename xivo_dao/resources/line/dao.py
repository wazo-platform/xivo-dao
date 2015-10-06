# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.exception import DataError

from xivo_dao.resources.line.persistor import LinePersistor


@daosession
def find_by(session, column, value):
    return LinePersistor(session).find_by(column, value)


@daosession
def search(session, **parameters):
    return LinePersistor(session).search(parameters)


@daosession
def get(session, line_id):
    return LinePersistor(session).get(line_id)


@daosession
def create(session, line):
    with commit_or_abort(session, DataError.on_create, 'Line'):
        return LinePersistor(session).create(line)


@daosession
def edit(session, line):
    with commit_or_abort(session, DataError.on_edit, 'Line'):
        LinePersistor(session).edit(line)


@daosession
def delete(session, line):
    with commit_or_abort(session, DataError.on_delete, 'Line'):
        return LinePersistor(session).delete(line)
