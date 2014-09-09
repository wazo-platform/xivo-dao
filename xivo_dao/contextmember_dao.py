# -*- coding: utf-8 -*-

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
from xivo_dao.alchemy.contextmember import ContextMember


@daosession
def add(session, contextmember):
    with commit_or_abort(session):
        session.add(contextmember)


@daosession
def delete_by_type_typeval(session, typename, typeval):
    with commit_or_abort(session):
        _request_type_typeval(session, typename, typeval).delete()


@daosession
def get_by_type_typeval(session, typename, typeval):
    return _request_type_typeval(session, typename, typeval).first()


def _request_type_typeval(session, typename, typeval):
    return session.query(ContextMember).filter(ContextMember.type == typename)\
                                       .filter(ContextMember.typeval == typeval)
