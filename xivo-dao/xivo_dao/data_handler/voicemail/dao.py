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

from sqlalchemy.sql.expression import desc, asc, or_
from sqlalchemy.exc import SQLAlchemyError
from xivo_dao.alchemy.voicemail import Voicemail as VoicemailSchema
from xivo_dao.alchemy.usersip import UserSIP as UserSIPSchema
from xivo_dao.alchemy.userfeatures import UserFeatures as UserSchema
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.voicemail.model import db_converter, VoicemailOrder, Voicemail
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers.sysconfd_connector import SysconfdError
from xivo_dao.data_handler.exception import ElementNotExistsError, \
    ElementCreationError, ElementEditionError, ElementDeletionError
from xivo_dao.helpers.abstract_model import SearchResult
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


@daosession
def find_all(session, limit=None, skip=None, order=None, direction='asc', search=None):
    query = session.query(VoicemailSchema)

    query = count_query = _apply_search_criteria(query, search)
    query = _apply_order_and_direction(query, order, direction)
    query = _apply_skip_and_limit(query, skip, limit)

    items = _generate_items(query)
    total = _generate_total(count_query)

    return SearchResult(total, items)


def _generate_items(query):
    rows = query.all()

    if not rows:
        return []

    return [db_converter.to_model(row) for row in rows]


def _generate_total(query):
    return query.count()


def _apply_search_criteria(query, search):
    if search is None:
        return query

    criteria = []
    for column in Voicemail.SEARCH_COLUMNS:
        criteria.append(column.ilike('%%%s%%' % search))

    query = query.filter(or_(*criteria))
    return query


def _apply_order_and_direction(query, order, direction):
    if order is None:
        order = VoicemailOrder.number

    if direction == 'desc':
        order_expression = desc(order)
    else:
        order_expression = asc(order)

    query = query.order_by(order_expression)
    return query


def _apply_skip_and_limit(query, skip, limit):
    if skip is not None:
        query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    return query


@daosession
def find_all_timezone(session):
    rows = (session.query(StaticVoicemail.var_name)
           .filter(StaticVoicemail.category == 'zonemessages')
           .all())

    res = []
    for row in rows:
        res.append(row[0])

    return res


@daosession
def get_by_number_context(session, number, context):
    row = (session.query(VoicemailSchema)
           .filter(VoicemailSchema.mailbox == number)
           .filter(VoicemailSchema.context == context)
           .first())
    if not row:
        raise ElementNotExistsError('Voicemail', number=number, context=context)

    return db_converter.to_model(row)


@daosession
def get(session, voicemail_id):
    row = _get_voicemail_row(session, voicemail_id)
    return db_converter.to_model(row)


def _get_voicemail_row(session, voicemail_id):
    row = (session.query(VoicemailSchema)
           .filter(VoicemailSchema.uniqueid == voicemail_id)
           .first())

    if not row:
        raise ElementNotExistsError('Voicemail', uniqueid=voicemail_id)

    return row


@daosession
def create(session, voicemail):
    voicemail_row = db_converter.to_source(voicemail)
    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('voicemail', e)

    voicemail.id = voicemail_row.uniqueid

    return voicemail


@daosession
def edit(session, voicemail):
    session.begin()

    voicemail_row = _get_voicemail_row(voicemail.id)
    db_converter.update_source(voicemail_row, voicemail)

    session.begin()
    session.add(voicemail_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementEditionError('voicemail', e)


@daosession
def delete(session, voicemail):
    session.begin()
    try:
        _unlink_user_sip(session, voicemail.number_at_context)
        _unlink_user(session, voicemail.id)
        nb_row_affected = _delete_voicemail(session, voicemail.id)
        try:
            sysconfd_connector.delete_voicemail_storage(voicemail.context, voicemail.number)
        except Exception as e:
            session.rollback()
            raise SysconfdError(str(e))
        else:
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('voicemail', e)

    if nb_row_affected == 0:
        raise ElementDeletionError('voicemail', 'voicemail_id %s not exist' % voicemail.id)


def _unlink_user_sip(session, number_at_context):
    (session.query(UserSIPSchema)
     .filter(UserSIPSchema.mailbox == number_at_context)
     .update({'mailbox': None}))


def _unlink_user(session, voicemail_id):
    (session.query(UserSchema)
     .filter(UserSchema.voicemailid == voicemail_id)
     .update({'voicemailid': None}))


def _delete_voicemail(session, voicemail_id):
    return (session.query(VoicemailSchema)
            .filter(VoicemailSchema.uniqueid == voicemail_id)
            .delete())
