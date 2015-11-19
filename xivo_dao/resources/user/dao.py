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

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.user.persistor import UserPersistor
from xivo_dao.resources.user.search import user_search
from xivo_dao.resources.user.view import user_view
from xivo_dao.resources.user.fixes import UserFixes


@daosession
def search(session, **parameters):
    return UserPersistor(session, user_view, user_search).search(parameters)


@daosession
def get(session, user_id):
    return UserPersistor(session, user_view, user_search).get_by({'id': user_id})


@daosession
def get_by(session, **criteria):
    return UserPersistor(session, user_view, user_search).get_by(criteria)


@daosession
def find(session, user_id):
    return UserPersistor(session, user_view, user_search).find_by({'id': user_id})


@daosession
def find_by(session, **criteria):
    return UserPersistor(session, user_view, user_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return UserPersistor(session, user_view, user_search).find_all_by(criteria)


@daosession
def create(session, user):
    return UserPersistor(session, user_view, user_search).create(user)


@daosession
def edit(session, user):
    UserPersistor(session, user_view, user_search).create(user)
    UserFixes(session).fix(user.id)


@daosession
def delete(session, user):
    UserPersistor(session, user_view, user_search).delete(user)
