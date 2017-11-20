# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import ContextPersistor
from .search import context_search


@daosession
def search(session, **parameters):
    return ContextPersistor(session, context_search).search(parameters)


@daosession
def get(session, context_id):
    return ContextPersistor(session, context_search).get_by({'id': context_id})


@daosession
def get_by(session, **criteria):
    return ContextPersistor(session, context_search).get_by(criteria)


@daosession
def get_by_name(session, context_name):
    return ContextPersistor(session, context_search).get_by({'name': context_name})


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
