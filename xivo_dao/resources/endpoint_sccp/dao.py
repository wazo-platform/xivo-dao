# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.resources.endpoint_sccp.persistor import SccpPersistor


@daosession
def get(session, id):
    return SccpPersistor(session).get(id)


@daosession
def find(session, id):
    return SccpPersistor(session).find(id)


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
