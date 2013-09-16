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

import datetime

from sqlalchemy import func

from xivo_dao import stat_call_on_queue_dao
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatCallOnQueueDAO(DAOTestCase):

    tables = [StatCallOnQueue, StatQueue, StatAgent]

    def setUp(self):
        self.empty_tables()

    @staticmethod
    def _build_date(year, month, day, hour=0, minute=0, second=0, micro=0):
        return datetime.datetime(year, month, day, hour, minute, second, micro).strftime("%Y-%m-%d %H:%M:%S.%f")

    def _insert_queue_to_stat_queue(self, queue_name=None):
        queue_name = queue_name if queue_name else 'test_queue'
        queue = StatQueue()
        queue.name = queue_name

        self.add_me(queue)

        return queue.name, queue.id

    def _insert_agent_to_stat_agent(self, agent_name=None):
        agent_name = agent_name if agent_name else 'Agent/1234'
        agent = StatAgent()
        agent.name = agent_name

        self.add_me(agent)

        return agent.name, agent.id

    def test_add_two_queues(self):
        q1, _ = self._insert_queue_to_stat_queue('q1')
        q2, _ = self._insert_queue_to_stat_queue('q2')
        t1 = datetime.datetime(2012, 01, 01, 01, 01, 01)
        t2 = datetime.datetime(2012, 01, 01, 01, 01, 02)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid', t1, q1)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid', t2, q2)

    def test_add_full_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(self.session, 'callid', timestamp, queue_name)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_add_closed_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_closed_call(self.session, 'callid', timestamp, queue_name)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].time, timestamp)

    def test_add_abandoned_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_abandoned_call(self.session, 'callid', timestamp, queue_name, 42)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].waittime, 42)
        self.assertEqual(res[0].time, timestamp)

    def test_add_joinempty_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_joinempty_call(self.session, 'callid', timestamp, queue_name)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].time, timestamp)

    def test_add_leaveempty_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_leaveempty_call(self.session, 'callid', timestamp, queue_name, 13)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].waittime, 13)

    def test_add_timeout_call(self):
        timestamp = datetime.datetime(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_timeout_call(self.session, 'callid', timestamp, queue_name, 27)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].waittime, 27)

    def test_get_periodic_stats_full(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 01, 3, 0, 0)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(self.session, 'callid%s' % minute_increment, time, queue_name)

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_quarter_hour)

        self.assertEqual(stats_quarter_hour[start][queue_id]['full'], 1)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=15)][queue_id]['full'], 2)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=30)][queue_id]['full'], 1)

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_hour)

        self.assertEqual(stats_hour[start][queue_id]['full'], 4)

    def test_get_periodic_stats_closed(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 31, 23, 59, 59, 999999)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call(self.session, 'callid%s' % minute_increment, time, queue_name)

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_quarter_hour)

        self.assertEqual(stats_quarter_hour[start][queue_id]['closed'], 1)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=15)][queue_id]['closed'], 2)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=30)][queue_id]['closed'], 1)

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_hour)

        self.assertEqual(stats_hour[start][queue_id]['closed'], 4)

    def test_get_periodic_stats_total(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 31, 23, 59, 59, 999999)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(self.session, 'callid%s-full' % minute_increment, time, queue_name)

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call(self.session, 'callid%s-closed' % minute_increment, time, queue_name)

        other_call = StatCallOnQueue()
        other_call.time = start
        other_call.callid = 'other type'
        other_call.queue_id = queue_id
        other_call.status = 'abandoned'

        self.session.begin()
        self.session.add(other_call)
        self.session.commit()

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_quarter_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_quarter_hour)

        self.assertEqual(stats_quarter_hour[start][queue_id]['total'], 3)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=15)][queue_id]['total'], 4)
        self.assertEqual(stats_quarter_hour[start + datetime.timedelta(minutes=30)][queue_id]['total'], 2)

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(self.session, start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats_hour)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats_hour)

        self.assertEqual(stats_hour[start][queue_id]['total'], 9)

    def test_clean_table(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        queue_name, _ = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(self.session, 'callid%s' % minute_increment, time, queue_name)

        stat_call_on_queue_dao.clean_table(self.session)

        total = (self.session.query(func.count(StatCallOnQueue.callid))).first()[0]

        self.assertEqual(total, 0)

    def test_remove_after(self):
        stat_call_on_queue_dao.remove_after(self.session, datetime.datetime(2012, 1, 1))

        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(self.session, 'callid1', datetime.datetime(2012, 1, 1), queue_name)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid2', datetime.datetime(2012, 1, 2), queue_name)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid3', datetime.datetime(2012, 1, 3), queue_name)

        stat_call_on_queue_dao.remove_after(self.session, datetime.datetime(2012, 1, 2))

        callids = self.session.query(StatCallOnQueue.callid)
        self.assertEqual(callids.count(), 1)
        self.assertEqual(callids[0].callid, 'callid1')
