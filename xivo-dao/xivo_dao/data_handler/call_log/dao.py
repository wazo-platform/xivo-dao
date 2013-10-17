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
from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.data_handler.exception import ElementCreationError, ElementDeletionError
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.call_log.model import db_converter


@daosession
def find_all(session):
    call_log_rows = session.query(CallLogSchema).all()

    if not call_log_rows:
        return []
    return map(db_converter.to_model, call_log_rows)


@daosession
def find_all_in_period(session, start, end):
    call_log_rows = (session
                     .query(CallLogSchema)
                     .filter(CallLogSchema.date.between(start, end))
                     .all())

    if not call_log_rows:
        return []
    return map(db_converter.to_model, call_log_rows)


@daosession
def create_from_list(session, call_logs):
    session.begin()
    for call_log in call_logs:
        call_log_row = _create_call_log(session, call_log)
        _link_call_log(session, call_log, call_log_row)

    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('CallLog', e)


def _create_call_log(session, call_log):
    call_log_row = db_converter.to_source(call_log)
    session.add(call_log_row)
    return call_log_row


def _link_call_log(session, call_log, call_log_row):
    for cel_id in call_log.get_related_cels():
        cel_row = session.query(CELSchema).get(cel_id)
        call_log_row.cels.append(cel_row)


@daosession
def delete_all(session):
    session.begin()
    session.query(CallLogSchema).delete()
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('CallLog', e)


@daosession
def delete_from_list(session, call_log_ids):
    session.begin()
    for call_log_id in call_log_ids:
        (session
         .query(CallLogSchema)
         .filter(CallLogSchema.id == call_log_id)
         .delete())
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('CallLog', e)
