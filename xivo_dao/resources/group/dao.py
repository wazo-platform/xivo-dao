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

from .persistor import GroupPersistor
from .search import group_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return GroupPersistor(session, group_search).search(parameters)


@daosession
def get(session, group_id):
    return GroupPersistor(session, group_search).get_by({'id': group_id})


@daosession
def get_by(session, **criteria):
    return GroupPersistor(session, group_search).get_by(criteria)


@daosession
def find(session, group_id):
    return GroupPersistor(session, group_search).find_by({'id': group_id})


@daosession
def find_by(session, **criteria):
    return GroupPersistor(session, group_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return GroupPersistor(session, group_search).find_all_by(criteria)


@daosession
def create(session, group):
    return GroupPersistor(session, group_search).create(group)


@daosession
def edit(session, group):
    GroupPersistor(session, group_search).edit(group)


@daosession
def delete(session, group):
    GroupPersistor(session, group_search).delete(group)


@daosession
def associate_all_member_users(session, group, users):
    GroupPersistor(session, group_search).associate_all_member_users(group, users)
