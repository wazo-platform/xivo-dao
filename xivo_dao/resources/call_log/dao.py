# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from sqlalchemy import or_

from xivo_dao.alchemy.call_log import CallLog as CallLogSchema
from xivo_dao.alchemy.cel import CEL as CELSchema
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.helpers.db_manager import daosession
from xivo_dao.resources.call_log.model import db_converter


@daosession
def find_all(session):
    call_log_rows = session.query(CallLogSchema).all()

    if not call_log_rows:
        return []
    return map(db_converter.to_model, call_log_rows)


@daosession
def find_all_in_period(session, start=None, end=None):
    query = session.query(CallLogSchema)

    if start and end:
        query = query.filter(CallLogSchema.date.between(start, end))
    else:
        if start:
            query = query.filter(CallLogSchema.date >= start)
        if end:
            query = query.filter(CallLogSchema.date <= end)

    call_log_rows = query.all()

    if not call_log_rows:
        return []
    return map(db_converter.to_model, call_log_rows)


@daosession
def find_all_history_for_phones(session, identifiers, limit):
    call_log_rows = (session
                     .query(CallLogSchema)
                     .filter(or_(CallLogSchema.destination_line_identity.in_(identifiers),
                                 CallLogSchema.source_line_identity.in_(identifiers)))
                     .order_by(CallLogSchema.date.desc())
                     .limit(limit))

    return _converted_call_logs(call_log_rows)


@daosession
def create_from_list(session, call_logs):
    with flush_session(session):
        for call_log in call_logs:
            call_log_id = create_call_log(session, call_log)
            _link_call_log(session, call_log, call_log_id)


def create_call_log(session, call_log):
    call_log_row = db_converter.to_source(call_log)
    session.add(call_log_row)
    session.flush()
    return call_log_row.id


def _link_call_log(session, call_log, call_log_id):
    data_dict = {'call_log_id': int(call_log_id)}
    related_cels = call_log.get_related_cels()
    if related_cels:
        session.query(CELSchema).filter(
            CELSchema.id.in_(related_cels)
        ).update(data_dict, synchronize_session=False)


@daosession
def delete_all(session):
    with flush_session(session):
        session.query(CallLogSchema).delete()


@daosession
def delete_from_list(session, call_log_ids):
    with flush_session(session):
        for call_log_id in call_log_ids:
            (session
             .query(CallLogSchema)
             .filter(CallLogSchema.id == call_log_id)
             .delete())


def _converted_call_logs(rows):
    if not rows:
        return []
    return map(db_converter.to_model, rows)
