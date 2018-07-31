# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.resources.endpoint_sccp.persistor import SccpPersistor


@daosession
def get(session, sccp_id):
    return SccpPersistor(session).get(sccp_id)


@daosession
def find(session, sccp_id):
    return SccpPersistor(session).find(sccp_id)


@daosession
def search(session, **parameters):
    return SccpPersistor(session).search(parameters)


@daosession
def create(session, sccp):
    with flush_session(session):
        return SccpPersistor(session).create(sccp)


@daosession
def edit(session, sccp):
    with flush_session(session):
        return SccpPersistor(session).edit(sccp)


@daosession
def delete(session, sccp):
    with flush_session(session):
        return SccpPersistor(session).delete(sccp)
