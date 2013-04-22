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
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.helpers.db_manager import daosession

@daosession
def add_user_to_rightcall(session, userid, rightcallid):
    member = RightCallMember()
    member.rightcallid = rightcallid
    member.type = 'user'
    member.typeval = str(userid)
    session.begin()
    try:
        session.add(member)
        session.commit()
    except Exception:
        session.rollback()
        raise

@daosession
def get_by_userid(session, userid):
    return session.query(RightCallMember).filter(RightCallMember.type == 'user')\
                                         .filter(RightCallMember.typeval == str(userid))\
                                         .all()


@daosession
def delete_by_userid(session, userid):
    session.begin()
    try:
        session.query(RightCallMember).filter(RightCallMember.type == 'user')\
                                      .filter(RightCallMember.typeval == str(userid))\
                                      .delete()
        session.commit()
    except Exception:
        session.rollback()
        raise


