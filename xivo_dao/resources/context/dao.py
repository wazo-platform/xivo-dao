# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import ContextPersistor
from .search import context_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return ContextPersistor(session, context_search, tenant_uuids).search(parameters)


@daosession
def get(session, context_id, tenant_uuids=None):
    return ContextPersistor(session, context_search, tenant_uuids).get_by({'id': context_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return ContextPersistor(session, context_search, tenant_uuids).get_by(criteria)


@daosession
def get_by_name(session, context_name, tenant_uuids=None):
    return ContextPersistor(session, context_search, tenant_uuids).get_by({'name': context_name})


@daosession
def find(session, context_id):
    return ContextPersistor(session, context_search).find_by({'id': context_id})


@daosession
def find_by(session, **criteria):
    return ContextPersistor(session, context_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return ContextPersistor(session, context_search).find_all_by(criteria)


@daosession
def create(session, context):
    return ContextPersistor(session, context_search).create(context)


@daosession
def edit(session, context):
    ContextPersistor(session, context_search).edit(context)


@daosession
def delete(session, context):
    ContextPersistor(session, context_search).delete(context)


@daosession
def associate_contexts(session, context, contexts):
    ContextPersistor(session, context_search).associate_contexts(context, contexts)
