# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime as dt
from datetime import timedelta
from pytz import UTC

from hamcrest import assert_that
from hamcrest import contains_exactly
from sqlalchemy import func

from xivo_dao import stat_call_on_queue_dao
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.tests.test_dao import DAOTestCase


class TestStatCallOnQueueDAO(DAOTestCase):
    def _insert_queue_to_stat_queue(self, queue_name=None, tenant_uuid=None):
        queue_name = queue_name if queue_name else 'test_queue'
        queue = StatQueue()
        queue.name = queue_name
        queue.tenant_uuid = tenant_uuid or self.default_tenant.uuid

        self.add_me(queue)

        return queue.name, queue.id

    def _insert_agent_to_stat_agent(self, agent_name=None, tenant_uuid=None):
        agent_name = agent_name if agent_name else 'Agent/1234'
        agent = StatAgent()
        agent.name = agent_name
        agent.tenant_uuid = tenant_uuid or self.default_tenant.uuid

        self.add_me(agent)

        return agent.name, agent.id

    def test_add_two_queues(self):
        q1, _ = self._insert_queue_to_stat_queue('q1')
        q2, _ = self._insert_queue_to_stat_queue('q2')
        t1 = dt(2012, 1, 1, 1, 1, 1, tzinfo=UTC)
        t2 = dt(2012, 1, 1, 1, 1, 2, tzinfo=UTC)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid', t1, q1)
        stat_call_on_queue_dao.add_full_call(self.session, 'callid', t2, q2)

    def test_add_full_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(
            self.session, 'callid', timestamp, queue_name
        )

        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'

    def test_add_closed_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_closed_call(
            self.session, 'callid', timestamp, queue_name
        )

        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'
        assert res[0].time == timestamp

    def test_add_abandoned_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_abandoned_call(
            self.session, 'callid', timestamp, queue_name, 42
        )
        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'
        assert res[0].waittime == 42
        assert res[0].time == timestamp

    def test_add_joinempty_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_joinempty_call(
            self.session, 'callid', timestamp, queue_name
        )
        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'
        assert res[0].time == timestamp

    def test_add_leaveempty_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_leaveempty_call(
            self.session, 'callid', timestamp, queue_name, 13
        )
        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'
        assert res[0].waittime == 13

    def test_add_timeout_call(self):
        timestamp = dt(2012, 1, 2, 0, 0, 0, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_timeout_call(
            self.session, 'callid', timestamp, queue_name, 27
        )
        res = self.session.query(StatCallOnQueue).filter(
            StatCallOnQueue.callid == 'callid'
        )

        assert res[0].callid == 'callid'
        assert res[0].waittime == 27

    def test_get_periodic_stats_full(self):
        start = dt(2012, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = dt(2012, 1, 1, 3, 0, 0, tzinfo=UTC)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(
                self.session, f'callid{minute_increment}', time, queue_name
            )

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_quarter_hour)

        assert stats_quarter_hour[start][queue_id]['full'] == 1
        assert stats_quarter_hour[start + timedelta(minutes=15)][queue_id]['full'] == 2
        assert stats_quarter_hour[start + timedelta(minutes=30)][queue_id]['full'] == 1

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_hour)

        assert stats_hour[start][queue_id]['full'] == 4

    def test_get_periodic_stats_closed(self):
        start = dt(2012, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = dt(2012, 1, 31, 23, 59, 59, 999999, tzinfo=UTC)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call(
                self.session, f'callid{minute_increment}', time, queue_name
            )

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_quarter_hour)

        assert stats_quarter_hour[start][queue_id]['closed'] == 1
        assert (
            stats_quarter_hour[start + timedelta(minutes=15)][queue_id]['closed'] == 2
        )
        assert (
            stats_quarter_hour[start + timedelta(minutes=30)][queue_id]['closed'] == 1
        )

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_hour)

        assert stats_hour[start][queue_id]['closed'] == 4

    def test_get_periodic_stats_total(self):
        start = dt(2012, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = dt(2012, 1, 31, 23, 59, 59, 999999, tzinfo=UTC)

        queue_name, queue_id = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(
                self.session, f'callid{minute_increment}-full', time, queue_name
            )

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_closed_call(
                self.session, f'callid{minute_increment}-closed', time, queue_name
            )

        other_call = StatCallOnQueue()
        other_call.time = start
        other_call.callid = 'other type'
        other_call.stat_queue_id = queue_id
        other_call.status = 'abandoned'

        self.add_me(other_call)

        stats_quarter_hour = stat_call_on_queue_dao.get_periodic_stats_quarter_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_quarter_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_quarter_hour)

        assert stats_quarter_hour[start][queue_id]['total'] == 3
        assert stats_quarter_hour[start + timedelta(minutes=15)][queue_id]['total'] == 4
        assert stats_quarter_hour[start + timedelta(minutes=30)][queue_id]['total'] == 2

        stats_hour = stat_call_on_queue_dao.get_periodic_stats_hour(
            self.session, start, end
        )

        self.assertTrue(dt(2012, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 1, tzinfo=UTC) in stats_hour)
        self.assertTrue(dt(2012, 1, 1, 2, tzinfo=UTC) in stats_hour)

        assert stats_hour[start][queue_id]['total'] == 9

    def test_clean_table(self):
        start = dt(2012, 1, 1, 0, 0, 0, tzinfo=UTC)

        queue_name, _ = self._insert_queue_to_stat_queue()

        for minute_increment in [-5, 5, 15, 22, 35, 65, 120]:
            delta = timedelta(minutes=minute_increment)
            time = start + delta
            stat_call_on_queue_dao.add_full_call(
                self.session, f'callid{minute_increment}', time, queue_name
            )

        stat_call_on_queue_dao.clean_table(self.session)

        total = (self.session.query(func.count(StatCallOnQueue.callid))).first()[0]

        assert total == 0

    def test_remove_after(self):
        stat_call_on_queue_dao.remove_after(self.session, dt(2012, 1, 1, tzinfo=UTC))

        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(
            self.session, 'callid1', dt(2012, 1, 1, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, 'callid2', dt(2012, 1, 2, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, 'callid3', dt(2012, 1, 3, tzinfo=UTC), queue_name
        )

        stat_call_on_queue_dao.remove_after(self.session, dt(2012, 1, 2, tzinfo=UTC))

        callids = self.session.query(StatCallOnQueue.callid)
        assert callids.count() == 1
        assert callids[0].callid == 'callid1'

    def test_find_all_callid_between_date(self):
        callid1 = 'callid1'
        callid2 = 'callid2'
        callid3 = 'callid3'
        start = dt(2012, 1, 1, 10, 0, 0, tzinfo=UTC)
        end = dt(2012, 1, 1, 11, 59, 59, 999999, tzinfo=UTC)
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(
            self.session, callid1, dt(2012, 1, 1, 9, 34, 32, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid1, dt(2012, 1, 1, 10, 34, 32, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid2, dt(2012, 1, 1, 10, 11, 12, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid3, dt(2012, 1, 1, 10, 59, 59, tzinfo=UTC), queue_name
        )

        result = stat_call_on_queue_dao.find_all_callid_between_date(
            self.session, start, end
        )

        assert_that(result, contains_exactly(callid1, callid2, callid3))

    def test_that_find_all_callid_between_date_includes_calls_started_before_start(
        self,
    ):
        callid = '234235435'
        _, queue_id = self._insert_queue_to_stat_queue()
        _, agent_id = self._insert_agent_to_stat_agent()
        call = StatCallOnQueue(
            callid=callid,
            time=dt(2014, 1, 1, 10, 59, 59, tzinfo=UTC),
            ringtime=1,
            talktime=1,
            waittime=1,
            status='answered',
            stat_queue_id=queue_id,
            stat_agent_id=agent_id,
        )

        self.add_me(call)

        result = stat_call_on_queue_dao.find_all_callid_between_date(
            self.session,
            dt(2014, 1, 1, 11, 0, 0, tzinfo=UTC),
            dt(2014, 1, 1, 11, 59, 59, tzinfo=UTC),
        )

        assert_that(result, contains_exactly(callid))

    def test_remove_callid_before(self):
        callid1 = 'callid1'
        callid2 = 'callid2'
        callid3 = 'callid3'
        queue_name, _ = self._insert_queue_to_stat_queue()

        stat_call_on_queue_dao.add_full_call(
            self.session, callid1, dt(2012, 1, 1, 9, 34, 32, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid1, dt(2012, 1, 1, 10, 11, 12, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid1, dt(2012, 1, 1, 10, 59, 59, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid2, dt(2012, 1, 1, 10, 11, 12, tzinfo=UTC), queue_name
        )
        stat_call_on_queue_dao.add_full_call(
            self.session, callid3, dt(2012, 1, 1, 11, 22, 59, tzinfo=UTC), queue_name
        )

        stat_call_on_queue_dao.remove_callids(self.session, [callid1, callid2, callid3])

        callids = self.session.query(StatCallOnQueue.callid)
        assert callids.count() == 0
