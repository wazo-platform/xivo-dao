# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.alchemy.extension import Extension
from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession


@daosession
def exten_by_name(session, funckey_name):
    exten = session.query(Extension.exten).filter(Extension.typeval == funckey_name).first()
    if exten is None:
        return ''
    return exten[0]


@daosession
def create(session, exten):
    with commit_or_abort(session):
        session.add(exten)


@daosession
def get_by_exten(session, exten):
    return session.query(Extension).filter(Extension.exten == exten).first()


@daosession
def delete_by_exten(session, exten):
    with commit_or_abort(session):
        session.query(Extension).filter(Extension.exten == exten).delete()
