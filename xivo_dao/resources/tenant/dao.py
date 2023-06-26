# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import Persistor
from .search import tenant_search


@daosession
def find(session, resource_uuid, tenant_uuids=None):
    return Persistor(session, tenant_search, tenant_uuids).find_by({'uuid': resource_uuid})


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, tenant_search, tenant_uuids).find_all_by(criteria)


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, tenant_search, tenant_uuids).find_by(criteria)


@daosession
def get(session, resource_uuid, tenant_uuids=None):
    return Persistor(session, tenant_search, tenant_uuids).get_by({'uuid': resource_uuid})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, tenant_search, tenant_uuids).get_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return Persistor(session, tenant_search, tenant_uuids).search(parameters)


@daosession
def delete(session, tenant):
    Persistor(session, tenant_search).delete(tenant)
