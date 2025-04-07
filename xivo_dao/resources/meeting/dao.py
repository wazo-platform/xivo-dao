# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from .persistor import Persistor
from .search import meeting_search


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, meeting_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, meeting_search, tenant_uuids).find_all_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return Persistor(session, meeting_search, tenant_uuids).search(parameters)


@daosession
def get(session, meeting_uuid, tenant_uuids=None):
    return Persistor(session, meeting_search, tenant_uuids).get_by(
        {'uuid': meeting_uuid},
    )


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, meeting_search, tenant_uuids).get_by(criteria)


@daosession
def create(session, meeting):
    with flush_session(session):
        return Persistor(session, meeting_search).create(meeting)


@daosession
def edit(session, meeting):
    with flush_session(session):
        Persistor(session, meeting_search).edit(meeting)
        if not meeting.require_authorization:
            for authorization in meeting.meeting_authorizations:
                if authorization.status == 'pending':
                    authorization.status = 'accepted'


@daosession
def delete(session, meeting):
    with flush_session(session):
        return Persistor(session, meeting_search).delete(meeting)
