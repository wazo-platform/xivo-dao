# -*- coding: utf-8 -*-

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


from xivo_dao.resources.ivr.persistor import IVRPersistor
from xivo_dao.resources.ivr.search import ivr_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return IVRPersistor(session, ivr_search).search(parameters)


@daosession
def get(session, ivr_id):
    return IVRPersistor(session, ivr_search).get_by({'id': ivr_id})


@daosession
def get_by(session, **criteria):
    return IVRPersistor(session, ivr_search).get_by(criteria)


@daosession
def find(session, ivr_id):
    return IVRPersistor(session, ivr_search).find_by({'id': ivr_id})


@daosession
def find_by(session, **criteria):
    return IVRPersistor(session, ivr_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IVRPersistor(session, ivr_search).find_all_by(criteria)


@daosession
def create(session, ivr):
    return IVRPersistor(session, ivr_search).create(ivr)


@daosession
def edit(session, ivr):
    IVRPersistor(session, ivr_search).edit(ivr)


@daosession
def delete(session, ivr):
    IVRPersistor(session, ivr_search).delete(ivr)
