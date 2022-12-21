# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
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
    confd_queues_by_name = {queue['name']: queue for queue in confd_queues}
    _mark_recreated_queues_with_same_name_as_deleted(session, confd_queues_by_name)
    _mark_non_confd_queues_as_deleted(session, confd_queues)
    _create_missing_queues(session, queuelog_queues, confd_queues_by_name, master_tenant)
    _rename_deleted_queues_with_duplicate_name(session, confd_queues_by_name)


def _mark_recreated_queues_with_same_name_as_deleted(session, confd_queues_by_name):
    db_queue_query = session.query(StatQueue).filter(StatQueue.deleted.is_(False))
    db_queues_by_name = {queue.name: queue for queue in db_queue_query.all()}

    confd_queue_names = set(list(confd_queues_by_name.keys()))
    db_queue_names = set(list(db_queues_by_name.keys()))

    not_missing_queues = confd_queue_names.intersection(db_queue_names)
    for queue_name in not_missing_queues:
        confd_queue = confd_queues_by_name[queue_name]
        db_queue = db_queues_by_name[queue_name]
        if db_queue.queue_id != confd_queue['id']:
            db_queue.deleted = True
            session.flush()


def _mark_non_confd_queues_as_deleted(session, confd_queues):
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
    session.flush()


def _create_missing_queues(session, queuelog_queues, confd_queues_by_name, master_tenant):
    new_queue_names = set(confd_queues_by_name.keys())
    db_queue_query = session.query(StatQueue).filter(StatQueue.deleted.is_(False))
    old_queue_names = set(queue.name for queue in db_queue_query.all())
    missing_queues = list(new_queue_names - old_queue_names)
    for queue_name in missing_queues:
        queue = confd_queues_by_name[queue_name]
        new_queue = StatQueue()
        new_queue.name = queue_name
        new_queue.tenant_uuid = queue['tenant_uuid']
        new_queue.queue_id = queue['id']
        new_queue.deleted = False
        session.add(new_queue)
        session.flush()

    db_queue_query = session.query(StatQueue).filter(StatQueue.deleted.is_(True))
    old_queue_names = set(queue.name for queue in db_queue_query.all())
    missing_queues = list(set(queuelog_queues) - old_queue_names - new_queue_names)
    for queue_name in missing_queues:
        new_queue = StatQueue()
        new_queue.name = queue_name
        new_queue.tenant_uuid = master_tenant
        new_queue.deleted = True
        session.add(new_queue)
        session.flush()


def _rename_deleted_queues_with_duplicate_name(session, confd_queues_by_name):
    db_queue_query = session.query(StatQueue).filter(StatQueue.deleted.is_(True))
    for queue in db_queue_query.all():
        if queue.name in confd_queues_by_name:
            queue.name = _find_next_available_name(session, queue.name)
            session.flush()


def _find_next_available_name(session, name):
    query = session.query(StatQueue).filter(StatQueue.name == name)
    if query.first():
        next_name = '{}_'.format(name)
        return _find_next_available_name(session, next_name)
    return name


def clean_table(session):
    session.query(StatQueue).delete()
