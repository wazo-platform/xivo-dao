# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from .persistor import IAXPersistor


@daosession
def find_by(session, **criteria):
    return IAXPersistor(session).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return IAXPersistor(session).find_all_by(criteria)


@daosession
def search(session, **parameters):
    return IAXPersistor(session).search(parameters)


@daosession
def get(session, iax_id):
    return IAXPersistor(session).get(iax_id)


@daosession
def create(session, iax):
    with flush_session(session):
        return IAXPersistor(session).create(iax)


@daosession
def edit(session, iax):
    with flush_session(session):
        IAXPersistor(session).edit(iax)


@daosession
def delete(session, iax):
    with flush_session(session):
        return IAXPersistor(session).delete(iax)
