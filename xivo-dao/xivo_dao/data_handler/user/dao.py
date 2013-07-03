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
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementEditionError, ElementCreationError, ElementDeletionError


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
    res = (session.query(UserSchema)
                 .filter(UserSchema.firstname == firstname)
                 .filter(UserSchema.lastname == lastname)
                 .first())
    if not res:
        return None

    return User.from_data_source(res)


@daosession
def get(session, user_id):
    res = _new_query(session).filter(UserSchema.id == user_id).first()
    if not res:
        raise ElementNotExistsError('User', id=user_id)

    return User.from_data_source(res)


@daosession
def get_by_number_context(session, number, context):
    res = (_new_query(session)
           .filter(LineSchema.iduserfeatures == UserSchema.id)
           .filter(LineSchema.context == context)
           .filter(LineSchema.number == number)
           .filter(LineSchema.commented == 0)
           .first())

    if not res:
        raise ElementNotExistsError('User', number=number, context=context)

    return User.from_data_source(res)


@daosession
def create(session, user):
    user_row = user.to_data_source(UserSchema)
    session.begin()
    session.add(user_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('User', e)

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
        raise ElementEditionError('User', e)

    if nb_row_affected == 0:
        raise ElementEditionError('User', 'No now affected, probably user_id %s not exsit' % user.id)

    return nb_row_affected


@daosession
def delete(session, user):
    session.begin()
    try:
        nb_row_affected = _delete_user(session, user.id)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('User', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('User', 'No now affected, probably user_id %s not exsit' % user.id)

    return nb_row_affected


def _delete_user(session, user_id):
    result = (session.query(UserSchema) .filter(UserSchema.id == user_id) .delete())
    (session.query(QueueMember).filter(QueueMember.usertype == 'user')
                               .filter(QueueMember.userid == user_id)
                               .delete())
    (session.query(RightCallMember).filter(RightCallMember.type == 'user')
                                  .filter(RightCallMember.typeval == str(user_id))
                                  .delete())
    (session.query(Callfiltermember).filter(Callfiltermember.type == 'user')
                                    .filter(Callfiltermember.typeval == str(user_id))
                                    .delete())
    (session.query(Dialaction).filter(Dialaction.category == 'user')
                              .filter(Dialaction.categoryval == str(user_id))
                              .delete())
    (session.query(PhoneFunckey).filter(PhoneFunckey.iduserfeatures == user_id).delete())
    (session.query(SchedulePath).filter(SchedulePath.path == 'user')
                                .filter(SchedulePath.pathid == user_id)
                                .delete())
    return result


def _new_query(session):
    return session.query(UserSchema).filter(UserSchema.commented == 0)
