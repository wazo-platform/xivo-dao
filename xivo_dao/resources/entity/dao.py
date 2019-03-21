# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.entity.persistor import EntityPersistor
from xivo_dao.resources.entity.search import entity_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return EntityPersistor(session, entity_search, tenant_uuids).search(parameters)


@daosession
def get(session, entity_id, tenant_uuids=None):
    return EntityPersistor(session, entity_search, tenant_uuids).get_by({'id': entity_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return EntityPersistor(session, entity_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, entity_id, tenant_uuids=None):
    return EntityPersistor(session, entity_search, tenant_uuids).find_by({'id': entity_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return EntityPersistor(session, entity_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return EntityPersistor(session, entity_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, entity):
    return EntityPersistor(session, entity_search).create(entity)


@daosession
def edit(session, entity):
    EntityPersistor(session, entity_search).edit(entity)


@daosession
def delete(session, entity):
    EntityPersistor(session, entity_search).delete(entity)
