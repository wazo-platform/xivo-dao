# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session


from .persistor import ExternalAppPersistor
from .search import external_app_search


def _persistor(tenant_uuids=None):
    return ExternalAppPersistor(Session, external_app_search, tenant_uuids)


def search(tenant_uuids=None, **parameters):
    return _persistor(tenant_uuids).search(parameters)


def get(external_app_name, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'name': external_app_name})


def get_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).get_by(criteria)


def find(external_app_name, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'name': external_app_name})


def find_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_by(criteria)


def find_all_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_all_by(criteria)


def create(external_app):
    return _persistor().create(external_app)


def edit(external_app):
    _persistor().edit(external_app)


def delete(external_app):
    _persistor().delete(external_app)
