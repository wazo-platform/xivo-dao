# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import daosession
from xivo_dao.alchemy.cel import CEL as CELSchema


@daosession
def find_last_unprocessed(session, limit=None, older=None):
    subquery = (session
                .query(CELSchema.linkedid)
                .filter(CELSchema.call_log_id == None)
                .order_by(CELSchema.eventtime.desc()))
    if limit:
        subquery = subquery.limit(limit)
    elif older:
        subquery = subquery.filter(CELSchema.eventtime >= older)

    linked_ids = subquery.subquery()

    cel_rows = (session
                .query(CELSchema)
                .filter(CELSchema.linkedid.in_(linked_ids))
                .order_by(CELSchema.eventtime.desc())
                .all())
    cel_rows.reverse()
    return cel_rows


@daosession
def find_from_linked_id(session, linked_id):
    cel_rows = (session
                .query(CELSchema)
                .filter(CELSchema.linkedid == linked_id)
                .order_by(CELSchema.eventtime.asc())
                .all())
    return cel_rows
