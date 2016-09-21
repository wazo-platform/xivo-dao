# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Avencall
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

from sqlalchemy import and_

from xivo_dao.alchemy.user import User
from xivo_dao.alchemy.entity import Entity
from xivo_dao.helpers.db_manager import daosession


@daosession
def check_username_password(session, username, password):
    row = session.query(User).filter(and_(User.login == username,
                                          User.passwd == password,
                                          User.valid == 1)).first()

    return row is not None


@daosession
def get_admin_entity(session, username):
    filter_ = and_(
        User.login == username,
        User.valid == 1,
    )
    return session.query(Entity.name).join(User).filter(filter_).scalar()

@daosession
def get_admin_id(session, username):
    return session.query(User.id).filter(and_(User.login == username,
                                              User.valid == 1)).scalar()
