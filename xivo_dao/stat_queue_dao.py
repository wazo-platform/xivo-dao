# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import distinct
from sqlalchemy.sql.expression import or_
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_manager import daosession


@daosession
def _get(session, queue_id):
    return session.query(StatQueue).filter(StatQueue.id == queue_id)[0]


@daosession
def id_from_name(session, queue_name):
    res = session.query(StatQueue).filter(StatQueue.name == queue_name)
    if res.count() == 0:
        raise LookupError('No such queue')
    return res[0].id


def insert_if_missing(session, queuelog_queues, confd_queues, master_tenant):
    new_queue_names = set(queuelog_queues + [queue['name'] for queue in confd_queues])
    old_queue_names = set(r[0] for r in session.query(distinct(StatQueue.name)))

    new_queues_by_name = {queue['name']: queue for queue in confd_queues}
    missing_queues = list(new_queue_names - old_queue_names)

    for queue_name in missing_queues:
        queue = new_queues_by_name.get(queue_name, {})
        new_queue = StatQueue()
        new_queue.name = queue_name
        new_queue.tenant_uuid = queue.get('tenant_uuid') or master_tenant
        new_queue.queue_id = queue.get('id')
        session.add(new_queue)

    active_queue_ids = set([queue['id'] for queue in confd_queues])
    all_queue_ids = set(r[0] for r in session.query(distinct(StatQueue.queue_id)))
    deleted_queues = [queue for queue in list(all_queue_ids - active_queue_ids) if queue]
    (
        session.query(StatQueue)
        .filter(
            or_(
                StatQueue.queue_id.in_(deleted_queues),
                StatQueue.queue_id.is_(None),
            )
        )
        .update({'deleted': True}, synchronize_session=False)

    )


def clean_table(session):
    session.query(StatQueue).delete()
