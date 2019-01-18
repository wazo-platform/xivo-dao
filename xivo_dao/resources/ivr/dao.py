# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import IVRPersistor
from .search import ivr_search


@daosession
def search(session, **parameters):
    return IVRPersistor(session, ivr_search).search(parameters)


@daosession
def get(session, ivr_id, tenant_uuids=None):
    return IVRPersistor(session, ivr_search, tenant_uuids).get_by({'id': ivr_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return IVRPersistor(session, ivr_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, ivr_id, tenant_uuids=None):
    return IVRPersistor(session, ivr_search, tenant_uuids).find_by({'id': ivr_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return IVRPersistor(session, ivr_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IVRPersistor(session, ivr_search).find_all_by(criteria)


@daosession
def create(session, ivr):
    return IVRPersistor(session, ivr_search).create(ivr)


@daosession
def edit(session, ivr):
    IVRPersistor(session, ivr_search).edit(ivr)


@daosession
def delete(session, ivr):
    IVRPersistor(session, ivr_search).delete(ivr)
