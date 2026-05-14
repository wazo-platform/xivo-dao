# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.stat_agent_periodic import StatAgentPeriodic


def insert_stats(session, period_stats, period_start):
    for (stat_agent_id, stat_queue_id), times in period_stats.items():
        entry = StatAgentPeriodic(
            time=period_start,
            login_time=times['login_time'] if 'login_time' in times else '00:00:00',
            pause_time=times['pause_time'] if 'pause_time' in times else '00:00:00',
            wrapup_time=times['wrapup_time'] if 'wrapup_time' in times else '00:00:00',
            stat_agent_id=stat_agent_id,
            stat_queue_id=stat_queue_id,
        )

        session.add(entry)


def clean_table(session):
    session.query(StatAgentPeriodic).delete()


def remove_after(session, date):
    session.query(StatAgentPeriodic).filter(StatAgentPeriodic.time >= date).delete()
