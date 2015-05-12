# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.helpers.db_utils import commit_or_abort
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctimain import CtiMain
from xivo_dao.data_handler.exception import DataError


@daosession
def is_live_reload_enabled(session):
    ctimain = session.query(CtiMain).first()
    return ctimain.live_reload_conf == 1


@daosession
def set_live_reload_status(session, data):
    value = 1 if data['enabled'] else 0
    with commit_or_abort(session, DataError.on_edit, 'Configuration'):
        session.query(CtiMain).update({'live_reload_conf': value})
