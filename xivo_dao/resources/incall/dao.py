# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.incall.persistor import IncallPersistor
from xivo_dao.resources.incall.search import incall_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return IncallPersistor(session, incall_search).search(parameters)


@daosession
def get(session, incall_id):
    return IncallPersistor(session, incall_search).get_by({'id': incall_id})


@daosession
def get_by(session, **criteria):
    return IncallPersistor(session, incall_search).get_by(criteria)


@daosession
def find(session, incall_id):
    return IncallPersistor(session, incall_search).find_by({'id': incall_id})


@daosession
def find_by(session, **criteria):
    return IncallPersistor(session, incall_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IncallPersistor(session, incall_search).find_all_by(criteria)


@daosession
def create(session, incall):
    return IncallPersistor(session, incall_search).create(incall)


@daosession
def edit(session, incall):
    IncallPersistor(session, incall_search).edit(incall)


@daosession
def delete(session, incall):
    IncallPersistor(session, incall_search).delete(incall)
