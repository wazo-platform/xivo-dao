# -*- coding: UTF-8 -*-
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

        self.session.add(queue)
        self.session.commit()

        return queue.name, queue.id

    def _insert_agent_to_stat_agent(self, agent_name=None):
        agent_name = agent_name if agent_name else 'Agent/1234'
        agent = StatAgent()
        agent.name = agent_name

        self.session.add(agent)
        self.session.commit()

        return agent.name, agent.id

    def test_add_two_queues(self):
        q1, _ = self._insert_queue_to_stat_queue('q1')
        q2, _ = self._insert_queue_to_stat_queue('q2')
        t1 = self._build_date(2012, 01, 01, 01, 01, 01)
        t2 = self._build_date(2012, 01, 01, 01, 01, 02)
        stat_call_on_queue_dao.add_full_call('callid', t1, q1)
        stat_call_on_queue_dao.add_full_call('callid', t2, q2)

    def test_add_full_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call('callid', timestamp, queue_name)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_add_closed_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_closed_call('callid', timestamp, queue_name)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_add_answered_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()
        agent_name, agent_id = self._insert_agent_to_stat_agent()

        stat_call_on_queue_dao.add_answered_call('callid', timestamp, queue_name, agent_name, 13, 22)

        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid').first()

        self.assertEqual(res.callid, 'callid')
        self.assertEqual(res.waittime, 13)
        self.assertEqual(res.talktime, 22)
        self.assertEqual(res.agent_id, agent_id)

    def test_add_abandoned_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_abandoned_call('callid', timestamp, queue_name, 42)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].waittime, 42)

    def test_add_joinempty_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_joinempty_call('callid', timestamp, queue_name)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')

    def test_add_leaveempty_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_leaveempty_call('callid', timestamp, queue_name, 13)
        res = self.session.query(StatCallOnQueue).filter(StatCallOnQueue.callid == 'callid')

        self.assertEqual(res[0].callid, 'callid')
        self.assertEqual(res[0].waittime, 13)

    def test_add_timeout_call(self):
        timestamp = self._build_date(2012, 01, 02, 00, 00, 00)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_timeout_call('callid', timestamp, queue_name, 27)
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
            stat_call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats)

        self.assertEqual(stats[start][queue_id]['full'], 4)

    def test_get_periodic_stats_closed(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 31, 23, 59, 59, 999999)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call('callid%s' % minute_increment, time, queue_name)

        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats)

        self.assertEqual(stats[start][queue_id]['closed'], 4)

    def test_get_periodic_stats_total(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)
        end = datetime.datetime(2012, 01, 31, 23, 59, 59, 999999)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call('callid%s-full' % minute_increment, time, queue_name)

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call('callid%s-closed' % minute_increment, time, queue_name)

        other_call = StatCallOnQueue()
        other_call.time = start
        other_call.callid = 'other type'
        other_call.queue_id = queue_id
        other_call.status = 'abandoned'

        self.session.add(other_call)
        self.session.commit()

        stats = stat_call_on_queue_dao.get_periodic_stats(start, end)

        self.assertTrue(datetime.datetime(2012, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 1) in stats)
        self.assertTrue(datetime.datetime(2012, 1, 1, 2) in stats)

        self.assertEqual(stats[start][queue_id]['total'], 9)

    def test_clean_table(self):
        start = datetime.datetime(2012, 01, 01, 00, 00, 00)

        queue_name, _ = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = datetime.timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call('callid%s' % minute_increment, time, queue_name)

        stat_call_on_queue_dao.clean_table()

        total = (self.session.query(func.count(StatCallOnQueue.callid))).first()[0]

        self.assertEqual(total, 0)
