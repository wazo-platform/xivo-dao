# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import Persistor
from .search import search_system


@daosession
def create(session, resource):
    return Persistor(session, search_system).create(resource)


@daosession
def create_blocklist(session, resource):
    return Persistor(session, search_system).create(resource)


@daosession
def delete(session, resource):
    Persistor(session, search_system).delete(resource)


@daosession
def edit(session, resource):
    Persistor(session, search_system).edit(resource)


@daosession
def find(session, uuid, tenant_uuids=None):
    return Persistor(session, search_system, tenant_uuids=tenant_uuids).find_by(
        {'uuid': uuid}
    )


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, search_system, tenant_uuids=tenant_uuids).find_all_by(
        criteria
    )


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, search_system, tenant_uuids=tenant_uuids).find_by(
        criteria
    )


@daosession
def get(session, uuid, tenant_uuids=None):
    return Persistor(session, search_system, tenant_uuids).get_by({'uuid': uuid})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, search_system, tenant_uuids).get_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return Persistor(session, search_system, tenant_uuids).search(parameters)
