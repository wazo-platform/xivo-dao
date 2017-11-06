# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session

from xivo_dao.resources.trunk.fixes import TrunkFixes
from xivo_dao.resources.trunk.persistor import TrunkPersistor
from xivo_dao.resources.trunk.search import trunk_search


@daosession
def search(session, **parameters):
    return TrunkPersistor(session, trunk_search).search(parameters)


@daosession
def get(session, trunk_id):
    return TrunkPersistor(session, trunk_search).get_by({'id': trunk_id})


@daosession
def get_by(session, **criteria):
    return TrunkPersistor(session, trunk_search).get_by(criteria)


@daosession
def find(session, trunk_id):
    return TrunkPersistor(session, trunk_search).find_by({'id': trunk_id})


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
