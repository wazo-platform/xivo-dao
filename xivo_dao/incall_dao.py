# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.db_manager import daosession
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer


@daosession
def get_by_exten(session, incall_exten):
    query = _new_query(session)
    return (query
            .filter(Incall.exten == incall_exten)
            .first())


def _new_query(session):
    return (session
            .query(Incall.id, Dialaction.action, Dialaction.actionarg1)
            .join((Dialaction, Incall.id == cast(Dialaction.categoryval, Integer)))
            .filter(Dialaction.category == u'incall')
            .filter(Dialaction.event == u'answer'))
