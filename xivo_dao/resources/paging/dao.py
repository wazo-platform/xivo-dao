# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from .persistor import PagingPersistor
from .search import paging_search


@daosession
def search(session, **parameters):
    return PagingPersistor(session, paging_search).search(parameters)


@daosession
def get(session, paging_id):
    return PagingPersistor(session, paging_search).get_by({'id': paging_id})


@daosession
def get_by(session, **criteria):
    return PagingPersistor(session, paging_search).get_by(criteria)


@daosession
def find(session, paging_id):
    return PagingPersistor(session, paging_search).find_by({'id': paging_id})


@daosession
def find_by(session, **criteria):
    return PagingPersistor(session, paging_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return PagingPersistor(session, paging_search).find_all_by(criteria)


@daosession
def create(session, paging):
    return PagingPersistor(session, paging_search).create(paging)


@daosession
def edit(session, paging):
    PagingPersistor(session, paging_search).edit(paging)


@daosession
def delete(session, paging):
    PagingPersistor(session, paging_search).delete(paging)
