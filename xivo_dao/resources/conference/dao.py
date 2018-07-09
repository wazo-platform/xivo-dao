# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_dao.helpers.db_manager import daosession

from .persistor import ConferencePersistor
from .search import conference_search


@daosession
def _persistor(session, tenant_uuids=None):
    return ConferencePersistor(session, conference_search, tenant_uuids)


def search(**parameters):
    return _persistor().search(parameters)


def get(conference_id, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'id': conference_id})


def get_by(**criteria):
    return _persistor().get_by(criteria)


def find(conference_id, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'id': conference_id})


def find_by(**criteria):
    return _persistor().find_by(criteria)


def find_all_by(**criteria):
    return _persistor().find_all_by(criteria)


def create(conference):
    return _persistor().create(conference)


def edit(conference):
    _persistor().edit(conference)


def delete(conference):
    _persistor().delete(conference)


@daosession
def exists(session, meetme_id):
    query = (session.query(MeetmeFeatures)
             .filter(MeetmeFeatures.id == meetme_id)
             )

    return query.count() > 0
