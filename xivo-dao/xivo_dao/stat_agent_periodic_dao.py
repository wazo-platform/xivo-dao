# -*- coding: UTF-8 -*-

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic


_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


def insert_stats(period_stats, period_start):
    for agent_id, login_time in period_stats.iteritems():
        entry = StatAgentPeriodic(
            time=period_start,
            login_time=login_time,
            agent_id=agent_id,
            )

        _session().add(entry)

    _session().commit()


def clean_table():
    _session().query(StatAgentPeriodic).delete()
    _session().commit()


def remove_after(date):
    _session().query(StatAgentPeriodic).filter(StatAgentPeriodic.time >= date).delete()
    _session().commit()
