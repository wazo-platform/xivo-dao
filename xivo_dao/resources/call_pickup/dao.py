# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import CallPickupPersistor
from .search import call_pickup_search


@daosession
def _persistor(session, tenant_uuids=None):
    return CallPickupPersistor(session, call_pickup_search, tenant_uuids)


@daosession
def search(session, **parameters):
    return _persistor().search(parameters)


@daosession
def get(session, call_pickup_id, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'id': call_pickup_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).get_by(criteria)


@daosession
def find(session, call_pickup_id, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'id': call_pickup_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return _persistor().find_all_by(criteria)


@daosession
def create(session, call_pickup):
    return _persistor().create(call_pickup)


@daosession
def edit(session, call_pickup):
    _persistor().edit(call_pickup)


@daosession
def delete(session, call_pickup):
    _persistor().delete(call_pickup)


@daosession
def associate_interceptor_users(session, call_pickup, users):
    _persistor().associate_interceptor_users(call_pickup, users)


@daosession
def associate_interceptor_groups(session, call_pickup, groups):
    _persistor().associate_interceptor_groups(call_pickup, groups)


@daosession
def associate_target_users(session, call_pickup, users):
    _persistor().associate_target_users(call_pickup, users)


@daosession
def associate_target_groups(session, call_pickup, groups):
    _persistor().associate_target_groups(call_pickup, groups)
