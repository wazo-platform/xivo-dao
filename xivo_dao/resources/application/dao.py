# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import ApplicationPersistor
from .search import application_search


@daosession
def _persistor(session, tenant_uuids=None):
    return ApplicationPersistor(session, application_search, tenant_uuids)


def search(tenant_uuids=None, **parameters):
    return _persistor(tenant_uuids).search(parameters)


def get(application_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).get_by({'uuid': str(application_uuid)})


def get_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).get_by(criteria)


def find(application_uuid, tenant_uuids=None):
    return _persistor(tenant_uuids).find_by({'uuid': str(application_uuid)})


def find_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_by(criteria)


def find_all_by(tenant_uuids=None, **criteria):
    return _persistor(tenant_uuids).find_all_by(criteria)


def create(application):
    return _persistor().create(application)


def edit(application):
    _persistor().edit(application)


def delete(application):
    _persistor().delete(application)
