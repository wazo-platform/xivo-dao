# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.endpoint_sip.persistor import SipPersistor


@daosession
def find_by(session, **criteria):
    return SipPersistor(session).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return SipPersistor(session).find_all_by(criteria)


@daosession
def search(session, **parameters):
    return SipPersistor(session).search(parameters)


@daosession
def get(session, line_id):
    return SipPersistor(session).get(line_id)


@daosession
def create(session, line):
    with flush_session(session):
        return SipPersistor(session).create(line)


@daosession
def edit(session, line):
    with flush_session(session):
        SipPersistor(session).edit(line)


@daosession
def delete(session, line):
    with flush_session(session):
        return SipPersistor(session).delete(line)
