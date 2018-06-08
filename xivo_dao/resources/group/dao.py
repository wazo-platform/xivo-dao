# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .persistor import GroupPersistor
from .search import group_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return GroupPersistor(session, group_search).search(parameters)


@daosession
def get(session, group_id):
    return GroupPersistor(session, group_search).get_by({'id': group_id})


@daosession
def get_by(session, **criteria):
    return GroupPersistor(session, group_search).get_by(criteria)


@daosession
def find(session, group_id):
    return GroupPersistor(session, group_search).find_by({'id': group_id})


@daosession
def find_by(session, **criteria):
    return GroupPersistor(session, group_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return GroupPersistor(session, group_search).find_all_by(criteria)


@daosession
def create(session, group):
    return GroupPersistor(session, group_search).create(group)


@daosession
def edit(session, group):
    GroupPersistor(session, group_search).edit(group)


@daosession
def delete(session, group):
    GroupPersistor(session, group_search).delete(group)


@daosession
def associate_all_member_users(session, group, members):
    GroupPersistor(session, group_search).associate_all_member_users(group, members)


@daosession
def associate_all_member_extensions(session, group, members):
    GroupPersistor(session, group_search).associate_all_member_extensions(group, members)


@daosession
def associate_call_permission(session, group, call_permission):
    GroupPersistor(session, group_search).associate_call_permission(group, call_permission)


@daosession
def dissociate_call_permission(session, group, call_permission):
    GroupPersistor(session, group_search).dissociate_call_permission(group, call_permission)
