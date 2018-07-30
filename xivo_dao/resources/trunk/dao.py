# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from .fixes import TrunkFixes
from .persistor import TrunkPersistor
from .search import trunk_search


@daosession
def search(session, **parameters):
    return TrunkPersistor(session, trunk_search).search(parameters)


@daosession
def get(session, trunk_id, tenant_uuids=None):
    return TrunkPersistor(session, trunk_search, tenant_uuids).get_by({'id': trunk_id})


@daosession
def get_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).get_by(criteria)


@daosession
def find(session, trunk_id, tenant_uuids=None):
    return TrunkPersistor(session, trunk_search, tenant_uuids).find_by({'id': trunk_id})


@daosession
def find_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).find_all_by(criteria)


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


@daosession
def associate_register_sip(session, trunk, register):
    TrunkPersistor(session, trunk_search).associate_register_sip(trunk, register)


@daosession
def dissociate_register_sip(session, trunk, register):
    TrunkPersistor(session, trunk_search).dissociate_register_sip(trunk, register)
