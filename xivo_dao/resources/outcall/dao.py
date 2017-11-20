# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from .persistor import OutcallPersistor
from .search import outcall_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return OutcallPersistor(session, outcall_search).search(parameters)


@daosession
def get(session, outcall_id):
    return OutcallPersistor(session, outcall_search).get_by({'id': outcall_id})


@daosession
def get_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).get_by(criteria)


@daosession
def find(session, outcall_id):
    return OutcallPersistor(session, outcall_search).find_by({'id': outcall_id})


@daosession
def find_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return OutcallPersistor(session, outcall_search).find_all_by(criteria)


@daosession
def create(session, outcall):
    return OutcallPersistor(session, outcall_search).create(outcall)


@daosession
def edit(session, outcall):
    OutcallPersistor(session, outcall_search).edit(outcall)


@daosession
def delete(session, outcall):
    OutcallPersistor(session, outcall_search).delete(outcall)
