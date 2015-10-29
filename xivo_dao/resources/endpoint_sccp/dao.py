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
