# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SwitchboardPersistor
from .search import switchboard_search


@daosession
def _persistor(session, tenant_uuids=None):
    return SwitchboardPersistor(session, switchboard_search, tenant_uuids=tenant_uuids)


def search(tenant_uuids=None, **parameters):
    return _persistor(tenant_uuids).search(parameters)


def get(switchboard_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'uuid': str(switchboard_uuid)})


def get_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).get_by(criteria)


def find(switchboard_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'uuid': str(switchboard_uuid)})


def find_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_by(criteria)


def find_all_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_all_by(criteria)


def create(switchboard):
    return _persistor().create(switchboard)


def edit(switchboard):
    return _persistor().edit(switchboard)


def delete(switchboard):
    _persistor().delete(switchboard)
