# -*- coding: utf-8 -*-

# Copyright (C) 2016 Francois Blackburn
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

from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.helpers.db_manager import daosession

from .persistor import ConferencePersistor
from .search import conference_search


@daosession
def search(session, **parameters):
    return ConferencePersistor(session, conference_search).search(parameters)


@daosession
def get(session, conference_id):
    return ConferencePersistor(session, conference_search).get_by({'id': conference_id})


@daosession
def get_by(session, **criteria):
    return ConferencePersistor(session, conference_search).get_by(criteria)


@daosession
def find(session, conference_id):
    return ConferencePersistor(session, conference_search).find_by({'id': conference_id})


@daosession
def find_by(session, **criteria):
    return ConferencePersistor(session, conference_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return ConferencePersistor(session, conference_search).find_all_by(criteria)


@daosession
def create(session, conference):
    return ConferencePersistor(session, conference_search).create(conference)


@daosession
def edit(session, conference):
    ConferencePersistor(session, conference_search).edit(conference)


@daosession
def delete(session, conference):
    ConferencePersistor(session, conference_search).delete(conference)


@daosession
def exists(session, meetme_id):
    query = (session.query(MeetmeFeatures)
             .filter(MeetmeFeatures.id == meetme_id)
             )

    return query.count() > 0
