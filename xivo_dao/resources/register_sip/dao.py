# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.register_sip.persistor import RegisterSIPPersistor
from xivo_dao.resources.register_sip.search import register_sip_search


@daosession
def search(session, **parameters):
    return RegisterSIPPersistor(session, register_sip_search).search(parameters)


@daosession
def get(session, register_sip_id):
    return RegisterSIPPersistor(session, register_sip_search).get_by({'id': register_sip_id})


@daosession
def find(session, register_sip_id):
    return RegisterSIPPersistor(session, register_sip_search).find_by({'id': register_sip_id})


@daosession
def create(session, register):
    return RegisterSIPPersistor(session, register_sip_search).create(register)


@daosession
def edit(session, register):
    RegisterSIPPersistor(session, register_sip_search).edit(register)


@daosession
def delete(session, register):
    RegisterSIPPersistor(session, register_sip_search).delete(register)
