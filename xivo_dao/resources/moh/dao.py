# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.moh.persistor import MOHPersistor
from xivo_dao.resources.moh.search import moh_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, tenant_uuids=None, **parameters):
    return MOHPersistor(session, moh_search, tenant_uuids).search(parameters)


@daosession
def get(session, moh_uuid, tenant_uuids=None):
    return MOHPersistor(session, moh_search, tenant_uuids).get_by({'uuid': moh_uuid})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return MOHPersistor(session, moh_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, moh_uuid, tenant_uuids=None):
    return MOHPersistor(session, moh_search, tenant_uuids).find_by({'uuid': moh_uuid})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return MOHPersistor(session, moh_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return MOHPersistor(session, moh_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, moh):
    return MOHPersistor(session, moh_search).create(moh)


@daosession
def edit(session, moh):
    MOHPersistor(session, moh_search).edit(moh)


@daosession
def delete(session, moh):
    MOHPersistor(session, moh_search).delete(moh)
