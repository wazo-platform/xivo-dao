# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.incall.persistor import IncallPersistor
from xivo_dao.resources.incall.search import incall_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, tenant_uuids=None, **parameters):
    return IncallPersistor(session, incall_search, tenant_uuids).search(parameters)


@daosession
def get(session, incall_id, tenant_uuids=None):
    return IncallPersistor(session, incall_search, tenant_uuids).get_by({'id': incall_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return IncallPersistor(session, incall_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, incall_id, tenant_uuids=None):
    return IncallPersistor(session, incall_search, tenant_uuids).find_by({'id': incall_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return IncallPersistor(session, incall_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return IncallPersistor(session, incall_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, incall):
    return IncallPersistor(session, incall_search).create(incall)


@daosession
def edit(session, incall):
    IncallPersistor(session, incall_search).edit(incall)


@daosession
def delete(session, incall):
    IncallPersistor(session, incall_search).delete(incall)
