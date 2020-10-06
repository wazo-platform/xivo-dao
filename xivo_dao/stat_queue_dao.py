# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import distinct
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
    new_queues = set(queuelog_queues)
    old_queues = set(r[0] for r in session.query(distinct(StatQueue.name)))

    missing_queues = list(new_queues - old_queues)
    queues_by_name = {queue['name']: queue for queue in confd_queues}

    for queue_name in missing_queues:
        new_queue = StatQueue()
        new_queue.name = queue_name
        new_queue.tenant_uuid = queues_by_name.get(queue_name, {}).get('tenant_uuid') or master_tenant
        new_queue.queue_id = queues_by_name.get(queue_name, {}).get('id')
        session.add(new_queue)


def clean_table(session):
    session.query(StatQueue).delete()
