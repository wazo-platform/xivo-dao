# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.line.persistor import LinePersistor
from xivo_dao.resources.line.fixes import LineFixes


@daosession
def find_by(session, tenant_uuids=None, **criteria):
    return LinePersistor(session, tenant_uuids).find_by(criteria)


@daosession
def find_all_by(session, tenant_uuids=None, **criteria):
    return LinePersistor(session, tenant_uuids).find_all_by(criteria)


@daosession
def search(session, tenant_uuids=None, **parameters):
    return LinePersistor(session, tenant_uuids).search(parameters)


@daosession
def get(session, line_id, tenant_uuids=None):
    return LinePersistor(session, tenant_uuids).get(line_id)


@daosession
def create(session, line):
    with flush_session(session):
        return LinePersistor(session).create(line)


@daosession
def edit(session, line):
    with flush_session(session):
        LinePersistor(session).edit(line)
        session.expire(line)
        LineFixes(session).fix_line(line.id)


@daosession
def delete(session, line):
    with flush_session(session):
        return LinePersistor(session).delete(line)
