# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.line.persistor import LinePersistor
from xivo_dao.resources.line.fixes import LineFixes


@daosession
def find_by(session, **criteria):
    return LinePersistor(session).find_by(criteria)


@daosession
def find_all_by(session, **criteria):
    return LinePersistor(session).find_all_by(criteria)


@daosession
def search(session, **parameters):
    return LinePersistor(session).search(parameters)


@daosession
def get(session, line_id):
    return LinePersistor(session).get(line_id)


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
