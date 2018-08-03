# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.callfiltermember import Callfiltermember as CallFilterMember
from xivo_dao.helpers.db_manager import daosession

from .persistor import CallFilterPersistor
from .search import call_filter_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).search(parameters)


@daosession
def get(session, call_filter_id, tenant_uuids=None):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).get_by({'id': call_filter_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, call_filter_id, tenant_uuids=None):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).find_by({'id': call_filter_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return CallFilterPersistor(session, call_filter_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, call_filter):
    return CallFilterPersistor(session, call_filter_search).create(call_filter)


@daosession
def edit(session, call_filter):
    CallFilterPersistor(session, call_filter_search).edit(call_filter)


@daosession
def delete(session, call_filter):
    CallFilterPersistor(session, call_filter_search).delete(call_filter)


@daosession
def associate_recipients(session, call_filter, recipients):
    CallFilterPersistor(session, call_filter_search).associate_recipients(call_filter, recipients)


@daosession
def associate_surrogates(session, call_filter, surrogates):
    CallFilterPersistor(session, call_filter_search).associate_surrogates(call_filter, surrogates)


@daosession
def member_exists(session, member_id):
    query = session.query(CallFilterMember).filter(CallFilterMember.id == member_id)
    return query.count() > 0


@daosession
def update_fallbacks(session, call_filter, fallbacks):
    CallFilterPersistor(session, call_filter_search).update_fallbacks(call_filter, fallbacks)
