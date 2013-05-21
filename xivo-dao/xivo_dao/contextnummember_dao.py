# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
from xivo_dao.alchemy.contextnummember import ContextNumMember


@daosession
def create(session, member):
    session.begin()
    try:
        if member.type == 'line':
            member.type = 'user'
        session.add(member)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def get_by_type_typeval_context(session, typename, typeval, context):
    return _request_type_typeval_context(session, typename, str(typeval), context).first()


def _request_type_typeval_context(session, typename, typeval, context):
    return (session.query(ContextNumMember).filter(ContextNumMember.type == typename)
                                           .filter(ContextNumMember.typeval == typeval)
                                           .filter(ContextNumMember.context == context))
