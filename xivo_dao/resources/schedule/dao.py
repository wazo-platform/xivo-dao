# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import daosession

from .persistor import SchedulePersistor
from .search import schedule_search


@daosession
def search(session, tenant_uuids=None, **parameters):
    return SchedulePersistor(session, schedule_search, tenant_uuids).search(parameters)


@daosession
def get(session, schedule_id, tenant_uuids=None):
    return SchedulePersistor(session, schedule_search, tenant_uuids).get_by({'id': schedule_id})


@daosession
def get_by(session, tenant_uuids=None, **criteria):
    return SchedulePersistor(session, schedule_search, tenant_uuids).get_by(criteria)


@daosession
def find(session, schedule_id, tenant_uuids=None):
    return SchedulePersistor(session, schedule_search, tenant_uuids).find_by({'id': schedule_id})


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return SchedulePersistor(session, schedule_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return SchedulePersistor(session, schedule_search, tenant_uuids).find_all_by(criteria)


@daosession
def create(session, schedule):
    return SchedulePersistor(session, schedule_search).create(schedule)


@daosession
def edit(session, schedule):
    SchedulePersistor(session, schedule_search).edit(schedule)


@daosession
def delete(session, schedule):
    SchedulePersistor(session, schedule_search).delete(schedule)
