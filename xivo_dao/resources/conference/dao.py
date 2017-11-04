# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

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
