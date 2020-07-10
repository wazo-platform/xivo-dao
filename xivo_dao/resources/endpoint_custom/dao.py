# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import flush_session

from .persistor import CustomPersistor
from .search import custom_search


def persistor(tenant_uuids=None):
    return CustomPersistor(Session, custom_search, tenant_uuids)


def get(custom_id, tenant_uuids=None, **ignored):
    return persistor(tenant_uuids).get(custom_id)


def find_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).find_by(criteria)


def find_all_by(tenant_uuids=None, **criteria):
    return persistor(tenant_uuids).find_all_by(criteria)


def search(tenant_uuids=None, **parameters):
    return persistor(tenant_uuids).search(parameters)


def create(custom):
    with flush_session(Session):
        return persistor().create(custom)


def edit(custom):
    with flush_session(Session):
        return persistor().edit(custom)


def delete(custom):
    with flush_session(Session):
        return persistor().delete(custom)
