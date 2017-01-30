# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.resources.moh.persistor import MOHPersistor
from xivo_dao.resources.moh.search import moh_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return MOHPersistor(session, moh_search).search(parameters)


@daosession
def get(session, moh_uuid):
    return MOHPersistor(session, moh_search).get_by({'uuid': moh_uuid})


@daosession
def get_by(session, **criteria):
    return MOHPersistor(session, moh_search).get_by(criteria)


@daosession
def find(session, moh_uuid):
    return MOHPersistor(session, moh_search).find_by({'uuid': moh_uuid})


@daosession
def find_by(session, **criteria):
    return MOHPersistor(session, moh_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return MOHPersistor(session, moh_search).find_all_by(criteria)


@daosession
def create(session, moh):
    return MOHPersistor(session, moh_search).create(moh)


@daosession
def edit(session, moh):
    MOHPersistor(session, moh_search).edit(moh)


@daosession
def delete(session, moh):
    MOHPersistor(session, moh_search).delete(moh)
