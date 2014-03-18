# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctiphonehints import CtiPhoneHints


@daosession
def get_config(session):
    res = {}
    hintsgroups = (session.query(CtiPhoneHintsGroup).all())
    for hintsgroup in hintsgroups:
        res[hintsgroup.name] = {}
        hints = get_hints_with_group_id(hintsgroup.id)
        for hint in hints:
            res[hintsgroup.name][hint.number] = {}
            res[hintsgroup.name][hint.number]['longname'] = hint.name
            res[hintsgroup.name][hint.number]['color'] = hint.color
    return res


@daosession
def get_hints_with_group_id(session, group_id):
    return session.query(CtiPhoneHints).filter(CtiPhoneHints.idgroup == group_id).all()
