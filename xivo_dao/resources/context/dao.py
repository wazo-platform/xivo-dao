# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from .persistor import ContextPersistor
from .search import context_search


@daosession
def search(session, **parameters):
    return ContextPersistor(session, context_search).search(parameters)


@daosession
def get(session, context_id):
    return ContextPersistor(session, context_search).get_by({'id': context_id})


@daosession
def get_by(session, **criteria):
    return ContextPersistor(session, context_search).get_by(criteria)


@daosession
def find(session, context_id):
    return ContextPersistor(session, context_search).find_by({'id': context_id})


@daosession
def find_by(session, **criteria):
    return ContextPersistor(session, context_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return ContextPersistor(session, context_search).find_all_by(criteria)


@daosession
def create(session, context):
    return ContextPersistor(session, context_search).create(context)


@daosession
def edit(session, context):
    ContextPersistor(session, context_search).edit(context)


@daosession
def delete(session, context):
    ContextPersistor(session, context_search).delete(context)
