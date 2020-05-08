# -*- coding: utf-8 -*-
# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from .persistor import SipPersistor
from .search import sip_search


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return SipPersistor(session, sip_search, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return SipPersistor(session, sip_search, tenant_uuids).find_all_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return SipPersistor(session, sip_search, tenant_uuids).search(parameters)


@daosession
def get(session, sip_uuid, tenant_uuids=None):
    return SipPersistor(session, sip_search, tenant_uuids).get_by({'uuid': sip_uuid})


@daosession
def create(session, sip):
    with flush_session(session):
        return SipPersistor(session, sip_search).create(sip)


@daosession
def edit(session, sip):
    with flush_session(session):
        SipPersistor(session, sip_search).edit(sip)


@daosession
def delete(session, sip):
    with flush_session(session):
        return SipPersistor(session, sip_search).delete(sip)
