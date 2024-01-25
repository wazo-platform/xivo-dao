# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy.orm.strategy_options import Load, loader_option

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.call_permission.persistor import CallPermissionPersistor
from xivo_dao.resources.call_permission.search import call_permission_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).search(parameters)


@daosession
def get(session, call_permission_id, tenant_uuids=None):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).get_by({'id': call_permission_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).get_by(criteria)


@daosession
def find(session, call_permission_id, tenant_uuids=None):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).find_by({'id': call_permission_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return CallPermissionPersistor(
        session, call_permission_search, tenant_uuids
    ).find_all_by(criteria)


@daosession
def create(session, call_permission):
    return CallPermissionPersistor(session, call_permission_search).create(
        call_permission
    )


@daosession
def edit(session, call_permission):
    CallPermissionPersistor(session, call_permission_search).edit(call_permission)


@daosession
def delete(session, call_permission):
    CallPermissionPersistor(session, call_permission_search).delete(call_permission)


@contextmanager
def query_options(*options: Load | loader_option):
    with CallPermissionPersistor.context_query_options(*options):
        yield
