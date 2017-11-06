# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.resources.ivr.persistor import IVRPersistor
from xivo_dao.resources.ivr.search import ivr_search

from xivo_dao.helpers.db_manager import daosession


@daosession
def search(session, **parameters):
    return IVRPersistor(session, ivr_search).search(parameters)


@daosession
def get(session, ivr_id):
    return IVRPersistor(session, ivr_search).get_by({'id': ivr_id})


@daosession
def get_by(session, **criteria):
    return IVRPersistor(session, ivr_search).get_by(criteria)


@daosession
def find(session, ivr_id):
    return IVRPersistor(session, ivr_search).find_by({'id': ivr_id})


@daosession
def find_by(session, **criteria):
    return IVRPersistor(session, ivr_search).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IVRPersistor(session, ivr_search).find_all_by(criteria)


@daosession
def create(session, ivr):
    return IVRPersistor(session, ivr_search).create(ivr)


@daosession
def edit(session, ivr):
    IVRPersistor(session, ivr_search).edit(ivr)


@daosession
def delete(session, ivr):
    IVRPersistor(session, ivr_search).delete(ivr)
