# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_dao.helpers.db_manager import daosession


@daosession
def exten_by_name(session, funckey_name):
    extens = [exten for exten, name in session.query(Extension.exten, Extension.name) if name == funckey_name]
    return extens[0] if extens else ''


@daosession
def create(session, exten):
    session.begin()
    try:
        session.add(exten)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def get_by_exten(session, exten):
    return session.query(Extension).filter(Extension.exten == exten).first()


@daosession
def delete_by_exten(session, exten):
    session.begin()
    try:
        session.query(Extension).filter(Extension.exten == exten).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise


