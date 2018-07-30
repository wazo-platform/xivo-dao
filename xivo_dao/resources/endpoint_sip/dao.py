# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.endpoint_sip.persistor import SipPersistor


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return SipPersistor(session, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return SipPersistor(session, tenant_uuids).find_all_by(criteria)


@daosession
def search(session, **parameters):
    return SipPersistor(session).search(parameters)


@daosession
def get(session, sip_id, tenant_uuids=None):
    return SipPersistor(session, tenant_uuids).get_by({'id': sip_id})


@daosession
def create(session, sip):
    with flush_session(session):
        return SipPersistor(session).create(sip)


@daosession
def edit(session, sip):
    with flush_session(session):
        SipPersistor(session).edit(sip)


@daosession
def delete(session, sip):
    with flush_session(session):
        return SipPersistor(session).delete(sip)
