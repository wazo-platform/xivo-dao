# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.sql import text
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_dao.helpers.db_manager import daosession


@daosession
def all_queues(session, order='number'):
    query = session.query(QueueFeatures)

    if order == 'number':
        query = query.order_by(QueueFeatures.number)

    return query.all()


@daosession
def get(session, queue_id):
    result = session.query(QueueFeatures).filter(QueueFeatures.id == queue_id).first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result


@daosession
def id_from_name(session, queue_name):
    result = session.query(QueueFeatures.id).filter(QueueFeatures.name == queue_name).first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result.id


@daosession
def queue_name(session, queue_id):
    result = session.query(QueueFeatures.name).filter(QueueFeatures.id == queue_id).first()
    if result is None:
        raise LookupError('No such queue')
    else:
        return result.name


@daosession
def is_user_member_of_queue(session, user_id, queue_id):
    statement = '''\
SELECT
    1 AS found
FROM
    queuefeatures
JOIN
    queuemember on queuemember.queue_name = queuefeatures.name
WHERE
    queuefeatures.id = :queue_id AND
    (queuemember.usertype = 'user' AND queuemember.userid = :user_id OR
     queuemember.usertype = 'agent' AND queuemember.userid = (
         SELECT
             agentid
         FROM
             userfeatures
         WHERE
             id = :user_id
        )
    )
'''
    row = (session
           .query('found')
           .from_statement(text(statement))
           .params(user_id=user_id, queue_id=queue_id)
           .first())
    return row is not None


def get_display_name_number(queue_id):
    queue = get(queue_id)
    return queue.displayname, queue.number
