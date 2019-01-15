# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import OutcallPersistor
from .search import outcall_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return OutcallPersistor(session, outcall_search, tenant_uuids).search(parameters)


@daosession
def get(session, outcall_id, tenant_uuids=None):
    return OutcallPersistor(session, outcall_search, tenant_uuids).get_by({'id': outcall_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return OutcallPersistor(session, outcall_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, outcall_id, tenant_uuids=None):
    return OutcallPersistor(session, outcall_search, tenant_uuids).find_by({'id': outcall_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return OutcallPersistor(session, outcall_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return OutcallPersistor(session, outcall_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, outcall):
    return OutcallPersistor(session, outcall_search).create(outcall)


@daosession
def edit(session, outcall):
    OutcallPersistor(session, outcall_search).edit(outcall)


@daosession
def delete(session, outcall):
    OutcallPersistor(session, outcall_search).delete(outcall)


@daosession
def associate_call_permission(session, outcall, call_permission):
    OutcallPersistor(session, outcall_search).associate_call_permission(outcall, call_permission)


@daosession
def dissociate_call_permission(session, outcall, call_permission):
    OutcallPersistor(session, outcall_search).dissociate_call_permission(outcall, call_permission)
