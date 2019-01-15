# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from .persistor import IAXPersistor
from .search import iax_search


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return IAXPersistor(session, iax_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return IAXPersistor(session, iax_search, tenant_uuids).find_all_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return IAXPersistor(session, iax_search, tenant_uuids).search(parameters)


@daosession
def get(session, iax_id, tenant_uuids=None):
    return IAXPersistor(session, iax_search, tenant_uuids).get(iax_id)


@daosession
def create(session, iax):
    with flush_session(session):
        return IAXPersistor(session, iax_search).create(iax)


@daosession
def edit(session, iax):
    with flush_session(session):
        IAXPersistor(session, iax_search).edit(iax)


@daosession
def delete(session, iax):
    with flush_session(session):
        return IAXPersistor(session, iax_search).delete(iax)
