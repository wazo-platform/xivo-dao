# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SwitchboardPersistor
from .search import switchboard_search


@daosession
def _persistor(session, tenant_uuids=None):
    return SwitchboardPersistor(session, switchboard_search, tenant_uuids=tenant_uuids)


@daosession
def search(session, **parameters):
    return _persistor().search(parameters)


@daosession
def get(session, switchboard_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'uuid': str(switchboard_uuid)})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).get_by(criteria)


@daosession
def find(session, switchboard_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'uuid': str(switchboard_uuid)})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return _persistor().find_all_by(criteria)


@daosession
def create(session, switchboard):
    return _persistor().create(switchboard)


@daosession
def edit(session, switchboard):
    return _persistor().edit(switchboard)


@daosession
def delete(session, switchboard):
    _persistor().delete(switchboard)
