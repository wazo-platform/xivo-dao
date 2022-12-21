# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from .persistor import Persistor
from .search import meeting_authorization_search


@daosession
def find_by(session, meeting_uuid, **criteria):
    return Persistor(session, meeting_authorization_search, meeting_uuid).find_by(criteria)


@daosession
def find_all_by(session, meeting_uuid, **criteria):
    return Persistor(session, meeting_authorization_search, meeting_uuid).find_all_by(criteria)


@daosession
def search(session, meeting_uuid, **parameters):
    return Persistor(session, meeting_authorization_search, meeting_uuid).search(parameters)


@daosession
def get(session, meeting_uuid, authorization_uuid, **criteria):
    criteria = dict(criteria)
    criteria['uuid'] = authorization_uuid
    return Persistor(session, meeting_authorization_search, meeting_uuid).get_by(criteria)


@daosession
def get_by(session, meeting_uuid, **criteria):
    return Persistor(session, meeting_authorization_search, meeting_uuid).get_by(criteria)


@daosession
def create(session, meeting_authorization):
    with flush_session(session):
        return Persistor(session, meeting_authorization_search).create(meeting_authorization)


@daosession
def edit(session, meeting_authorization):
    with flush_session(session):
        Persistor(session, meeting_authorization_search).edit(meeting_authorization)


@daosession
def delete(session, meeting_authorization):
    with flush_session(session):
        return Persistor(session, meeting_authorization_search).delete(meeting_authorization)
