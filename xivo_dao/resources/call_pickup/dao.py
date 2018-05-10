# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from .persistor import CallPickupPersistor
from .search import call_pickup_search


@daosession
def search(session, **parameters):
    return CallPickupPersistor(session, call_pickup_search).search(parameters)


@daosession
def get(session, call_pickup_id):
    return CallPickupPersistor(session, call_pickup_search).get_by({'id': call_pickup_id})


@daosession
def get_by(session, **criteria):
    return CallPickupPersistor(session, call_pickup_search).get_by(criteria)


@daosession
def find(session, call_pickup_id):
    return CallPickupPersistor(session, call_pickup_search).find_by({'id': call_pickup_id})


@daosession
def find_by(session, **criteria):
    return CallPickupPersistor(session, call_pickup_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return CallPickupPersistor(session, call_pickup_search).find_all_by(criteria)


@daosession
def create(session, call_pickup):
    return CallPickupPersistor(session, call_pickup_search).create(call_pickup)


@daosession
def edit(session, call_pickup):
    CallPickupPersistor(session, call_pickup_search).edit(call_pickup)


@daosession
def delete(session, call_pickup):
    CallPickupPersistor(session, call_pickup_search).delete(call_pickup)


@daosession
def associate_interceptor_users(session, call_pickup, users):
    CallPickupPersistor(session, call_pickup_search).associate_interceptor_users(call_pickup, users)


@daosession
def associate_interceptor_groups(session, call_pickup, groups):
    CallPickupPersistor(session, call_pickup_search).associate_interceptor_groups(call_pickup, groups)
