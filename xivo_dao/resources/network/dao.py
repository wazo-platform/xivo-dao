# -*- coding: utf-8 -*-
# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import Persistor
from .search import network_search


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, network_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return Persistor(session, network_search, tenant_uuids).find_all_by(criteria)


@daosession
def get(session, network_uuid, tenant_uuids=None):
    return Persistor(session, network_search, tenant_uuids).get_by(
        {'uuid': network_uuid},
    )


@daosession
def search(session, tenant_uuids=None, **parameters):
    return Persistor(session, network_search, tenant_uuids).search(parameters)


@daosession
def create(session, model):
    return Persistor(session, network_search).create(model)


@daosession
def edit(session, model):
    Persistor(session, network_search).edit(model)


@daosession
def delete(session, model):
    return Persistor(session, network_search).delete(model)
