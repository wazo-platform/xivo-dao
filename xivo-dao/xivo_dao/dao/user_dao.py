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

from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.linefeatures import LineFeatures as LineSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.models.user import User


class UserCreationError(IOError):

    def __init__(self, error):
        message = "error while creating user: %s" % unicode(error)
        IOError.__init__(self, message)


class UserEditionnError(IOError):

    def __init__(self, error):
        message = "error while editing user: %s" % unicode(error)
        IOError.__init__(self, message)


class UserDeletionError(IOError):

    def __init__(self, error):
        message = "error while deleting user: %s" % unicode(error)
        IOError.__init__(self, message)


@daosession
def find_all(session):
    res = session.query(UserSchema).all()

    if not res:
        return None

    tmp = []
    for user in res:
        tmp.append(User.from_data_source(user))

    return tmp


@daosession
def find_user(session, firstname, lastname):

    user = (session.query(UserSchema)
                 .filter(UserSchema.firstname == firstname)
                 .filter(UserSchema.lastname == lastname)
                 .first())

    if not user:
        return None

    return User.from_data_source(user)


@daosession
def get_user_by_id(session, user_id):
    user = _new_query(session).filter(UserSchema.id == user_id).first()

    if not user:
        raise LookupError('No user with id %s' % user_id)

    return User.from_data_source(user)


@daosession
def get_user_by_number_context(session, number, context):
    user = (_new_query(session)
        .filter(LineSchema.iduserfeatures == UserSchema.id)
        .filter(LineSchema.context == context)
        .filter(LineSchema.number == number)
        .filter(LineSchema.commented == 0)
        .first())

    if not user:
        raise LookupError('No user with number %s in context %s', (number, context))

    return User.from_data_source(user)


@daosession
def create(session, user):
    user_row = user.to_data_source(UserSchema)
    session.begin()
    session.add(user_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise UserCreationError(e)

    return user_row.id


@daosession
def edit(session, user):
    session.begin()
    nb_row_affected = (session.query(UserSchema)
                       .filter(UserSchema.id == user.id)
                       .update(user.to_data_dict()))

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise UserEditionnError(e)

    if nb_row_affected == 0:
        raise UserEditionnError('No now affected, probably user_id %s not exsit' % user.id)

    return nb_row_affected




def _new_query(session):
    return session.query(UserSchema).filter(UserSchema.commented == 0)
