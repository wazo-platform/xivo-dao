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

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.helpers.db_manager import daosession


@daosession
def add(session, dialaction):
    session.begin()
    try:
        session.add(dialaction)
        session.commit()
    except Exception:
        session.rollback()
        raise


@daosession
def get_by_userid(session, userid):
    return _request_by_userid(session, userid).all()


@daosession
def delete_by_userid(session, userid):
    session.begin()
    try:
        _request_by_userid(session, userid).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise


def _request_by_userid(session, userid):
    return (session.query(Dialaction).filter(Dialaction.category == 'user')
                                     .filter(Dialaction.categoryval == str(userid)))
