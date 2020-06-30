# -*- coding: utf-8 -*-
# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from .fixes import TrunkFixes
from .persistor import TrunkPersistor
from .search import trunk_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return TrunkPersistor(session, trunk_search, tenant_uuids).search(parameters)


@daosession
def get(session, trunk_id, tenant_uuids=None):
    return TrunkPersistor(session, trunk_search, tenant_uuids).get_by({'id': trunk_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return TrunkPersistor(session, trunk_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, trunk_id, tenant_uuids=None):
    return TrunkPersistor(session, trunk_search, tenant_uuids).find_by({'id': trunk_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return TrunkPersistor(session, trunk_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return TrunkPersistor(session, trunk_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, trunk):
    return TrunkPersistor(session, trunk_search).create(trunk)


@daosession
def edit(session, trunk):
    with flush_session(session):  # Maybe useless
        TrunkPersistor(session, trunk_search).edit(trunk)
        session.expire(trunk)
        TrunkFixes(session).fix(trunk.id)


@daosession
def delete(session, trunk):
    TrunkPersistor(session, trunk_search).delete(trunk)


@daosession
def associate_register_iax(session, trunk, register):
    TrunkPersistor(session, trunk_search).associate_register_iax(trunk, register)


@daosession
def dissociate_register_iax(session, trunk, register):
    TrunkPersistor(session, trunk_search).dissociate_register_iax(trunk, register)
