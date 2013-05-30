# -*- coding: utf-8 -*-

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

from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.models.user import User


def get_user_by_id(user_id):
    user = _new_query().filter(UserSchema.id == user_id).first()

    if not user:
        raise LookupError('No user with id %s' % user_id)

    return User.from_data_source(user)


def get_user_by_number_context(number, context):
    user = (_new_query()
        .filter(LineSchema.iduserfeatures == UserSchema.id)
        .filter(LineSchema.context == context)
        .filter(LineSchema.number == number)
        .filter(LineSchema.commented == 0)
        .first())

    if not user:
        raise LookupError('No user with number %s in context %s', (number, context))

    return User.from_data_source(user)


@daosession
def _new_query(session):
    return session.query(UserSchema).filter(UserSchema.commented == 0)
