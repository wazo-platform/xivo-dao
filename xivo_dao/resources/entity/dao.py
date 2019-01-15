# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.entity.persistor import EntityPersistor
from xivo_dao.resources.entity.search import entity_search


@daosession
def search(session, **parameters):
    return EntityPersistor(session, entity_search).search(parameters)


@daosession
def get(session, entity_id):
    return EntityPersistor(session, entity_search).get_by({'id': entity_id})


@daosession
def get_by(session, **criteria):
    return EntityPersistor(session, entity_search).get_by(criteria)


@daosession
def find(session, entity_id):
    return EntityPersistor(session, entity_search).find_by({'id': entity_id})


@daosession
def find_by(session, **criteria):
    return EntityPersistor(session, entity_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return EntityPersistor(session, entity_search).find_all_by(criteria)


@daosession
def create(session, entity):
    return EntityPersistor(session, entity_search).create(entity)


@daosession
def edit(session, entity):
    EntityPersistor(session, entity_search).edit(entity)


@daosession
def delete(session, entity):
    EntityPersistor(session, entity_search).delete(entity)
