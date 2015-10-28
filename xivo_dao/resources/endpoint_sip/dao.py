# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession

from xivo_dao.resources.endpoint_sip.persistor import SipPersistor


@daosession
def find_by(session, column, value):
    return SipPersistor(session).find_by(column, value)


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
