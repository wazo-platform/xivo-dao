# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import PagingPersistor
from .search import paging_search


@daosession
def search(session, **parameters):
    return PagingPersistor(session, paging_search).search(parameters)


@daosession
def get(session, paging_id):
    return PagingPersistor(session, paging_search).get_by({'id': paging_id})


@daosession
def get_by(session, **criteria):
    return PagingPersistor(session, paging_search).get_by(criteria)


@daosession
def find(session, paging_id, tenant_uuids=None):
    return PagingPersistor(session, paging_search, tenant_uuids).find_by({'id': paging_id})


@daosession
def find_by(session, **criteria):
    return PagingPersistor(session, paging_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return PagingPersistor(session, paging_search).find_all_by(criteria)


@daosession
def create(session, paging):
    return PagingPersistor(session, paging_search).create(paging)


@daosession
def edit(session, paging):
    PagingPersistor(session, paging_search).edit(paging)


@daosession
def delete(session, paging):
    PagingPersistor(session, paging_search).delete(paging)
