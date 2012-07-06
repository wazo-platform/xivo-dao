# -*- coding: UTF-8 -*-

from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy import dbconnection


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def _get(queue_id):
    return _session().query(StatQueue).filter(StatQueue.id == queue_id)[0]


def id_from_name(queue_name):
    res = _session().query(StatQueue).filter(StatQueue.name == queue_name)
    if res.count() == 0:
        raise LookupError('No such queue')
    return res[0].id
