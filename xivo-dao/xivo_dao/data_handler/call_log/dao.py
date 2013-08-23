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
from xivo_dao.data_handler.exception import ElementCreationError, ElementDeletionError
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.data_handler.call_log.model import CallLog


@daosession
def find_all(session):
    call_log_rows = session.query(CallLogSchema).all()

    if not call_log_rows:
        return []
    return map(CallLog.from_data_source, call_log_rows)


@daosession
def create_all(session, call_logs):
    session.begin()
    for call_log in call_logs:
        call_log_row = call_log.to_data_source(CallLogSchema)
        session.add(call_log_row)
        call_log.id = call_log_row.id
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementCreationError('CallLog', e)


@daosession
def delete_all(session):
    session.begin()
    session.query(CallLogSchema).delete()
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise ElementDeletionError('CallLog', e)
