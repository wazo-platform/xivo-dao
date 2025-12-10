# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import pathlib
from datetime import datetime as t

import pytz
from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    equal_to,
    has_properties,
)
from sqlalchemy import func, text

from xivo_dao import stat_call_on_queue_dao, stat_dao
from xivo_dao.alchemy.queue_log import QueueLog
from xivo_dao.alchemy.stat_agent import StatAgent
from xivo_dao.alchemy.stat_call_on_queue import StatCallOnQueue
from xivo_dao.alchemy.stat_queue import StatQueue
from xivo_dao.helpers.db_utils import flush_session
from xivo_dao.tests.test_dao import DAOTestCase

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class TestFillAnsweredCall(DAOTestCase):
    def setUp(self):
        DAOTestCase.setUp(self)
        self.callid = '1404377805.6457'
        self.enterqueue_event = QueueLog(
            time='2014-07-03 10:57:11.559080',
            callid=self.callid,
            queuename='swk_allemagne',
            agent='NONE',
            event='ENTERQUEUE',
            data2='00049242184770',
            data3='1',
        )
        self.connect_event = QueueLog(
            time='2014-07-03 10:57:19.461280',
            callid=self.callid,
            queuename='swk_allemagne',
            agent='Agent/448',
            event='CONNECT',
            data1='8',
            data2='1404377831.6460',
            data3='4',
        )
        self.complete_agent_event = QueueLog(
            time='2014-07-03 11:06:10.374302',
            callid=self.callid,
            queuename='swk_allemagne',
            agent='Agent/448',
            event='COMPLETEAGENT',
            data1='8',
            data2='531',
            data3='1',
        )

    def test_that_incomplete_calls_are_not_added(self):
        self.add_me_all([self.enterqueue_event, self.connect_event])

        stat_dao.fill_answered_calls(
            self.session, t(2014, 7, 3, 10, 0, 0), t(2014, 7, 3, 10, 59, 59, 999999)
        )

        count = (
            self.session.query(func.count(StatCallOnQueue.callid))
            .filter(StatCallOnQueue.callid == self.callid)
            .scalar()
        )

        assert_that(count, equal_to(0))

    def test_that_completed_calls_cannot_be_added_twice(self):
        # Given the same time boundaries, a call should be added and deleted to avoid duplicate calls
        # this test case shows an example with a call starting at 10 and ending at 11 that will only
        # be generated at 11 but that will not be deleted at 11
        begin, end = t(2014, 7, 3, 11, 0, 0), t(2014, 7, 3, 11, 59, 59, 999999)
        self.add_me_all(
            [self.enterqueue_event, self.connect_event, self.complete_agent_event]
        )

        stat_dao.fill_answered_calls(self.session, begin, end)

        callids = stat_call_on_queue_dao.find_all_callid_between_date(
            self.session, begin, end
        )
        stat_call_on_queue_dao.remove_callids(self.session, callids)

        stat_dao.fill_answered_calls(self.session, begin, end)

        count = (
            self.session.query(func.count(StatCallOnQueue.callid))
            .filter(StatCallOnQueue.callid == self.callid)
            .scalar()
        )

        assert_that(count, equal_to(1))

    def test_multitenant_answered_calls(self):
        begin = t(2014, 7, 3, 11, 0, 0)
        end = t(2014, 7, 3, 11, 59, 59, 999999)

        callid_1 = '1404377805.6457'
        callid_2 = '1404377805.6458'

        tenant_1 = self.add_tenant()
        tenant_2 = self.add_tenant()

        stat_queue_1 = StatQueue(
            name='q1',
            tenant_uuid=tenant_1.uuid,
            queue_id=1,
        )
        stat_queue_2 = StatQueue(
            name='q2',
            tenant_uuid=tenant_2.uuid,
            queue_id=2,
        )
        self.add_me_all([stat_queue_1, stat_queue_2])

        stat_agent_1 = StatAgent(
            name='Agent/1001',
            tenant_uuid=tenant_1.uuid,
            agent_id=1,
        )
        stat_agent_2 = StatAgent(
            name='Agent/1001',
            tenant_uuid=tenant_2.uuid,
            agent_id=2,
        )
        self.add_me_all([stat_agent_1, stat_agent_2])

        self.add_me_all(
            [
                # Call on tenant 1
                QueueLog(
                    time='2014-07-03 10:57:11.559080',
                    callid=callid_1,
                    queuename=stat_queue_1.name,
                    agent='NONE',
                    event='ENTERQUEUE',
                    data2='00049242184770',
                    data3='1',
                ),
                QueueLog(
                    time='2014-07-03 10:57:19.461280',
                    callid=callid_1,
                    queuename=stat_queue_1.name,
                    agent=stat_agent_1.name,
                    event='CONNECT',
                    data1='8',
                    data2='1404377831.6460',
                    data3='4',
                ),
                QueueLog(
                    time='2014-07-03 11:06:10.374302',
                    callid=callid_1,
                    queuename=stat_queue_1.name,
                    agent=stat_agent_1.name,
                    event='COMPLETEAGENT',
                    data1='8',
                    data2='531',
                    data3='1',
                ),
                # Call on tenant 2
                QueueLog(
                    time='2014-07-03 10:57:11.559080',
                    callid=callid_2,
                    queuename=stat_queue_2.name,
                    agent='NONE',
                    event='ENTERQUEUE',
                    data2='00049242184770',
                    data3='1',
                ),
                QueueLog(
                    time='2014-07-03 10:57:19.461280',
                    callid=callid_2,
                    queuename=stat_queue_2.name,
                    agent=stat_agent_2.name,
                    event='CONNECT',
                    data1='8',
                    data2='1404377831.6460',
                    data3='4',
                ),
                QueueLog(
                    time='2014-07-03 11:06:10.374302',
                    callid=callid_2,
                    queuename=stat_queue_2.name,
                    agent=stat_agent_2.name,
                    event='COMPLETEAGENT',
                    data1='8',
                    data2='531',
                    data3='1',
                ),
            ]
        )

        stat_dao.fill_answered_calls(self.session, begin, end)

        results = (
            self.session.query(StatCallOnQueue)
            .filter(StatCallOnQueue.callid.in_([callid_1, callid_2]))
            .all()
        )

        assert_that(
            results,
            contains_inanyorder(
                has_properties(
                    callid=callid_1,
                    stat_queue_id=stat_queue_1.id,
                    stat_agent_id=stat_agent_1.id,
                    status='answered',
                ),
                has_properties(
                    callid=callid_2,
                    stat_queue_id=stat_queue_2.id,
                    stat_agent_id=stat_agent_2.id,
                    status='answered',
                ),
            ),
        )


class TestFillSimpleCall(DAOTestCase):
    def setUp(self):
        DAOTestCase.setUp(self)
        self._create_functions()
        self.callid = '1404377805.6457'
        event = QueueLog(
            time=t(2020, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
            callid=self.callid,
            queuename='found_queue',
            event='FULL',
        )
        self.add_me(event)
        event = QueueLog(
            time=t(2020, 2, 1, tzinfo=pytz.UTC),
            callid=self.callid,
            queuename='ignored_queue',
            event='CLOSED',
        )
        self.add_me(event)

    def test_empty(self):
        start = t(1999, 1, 1)
        end = t(1999, 1, 31, 23, 59, 59, 999999)
        try:
            stat_dao.fill_simple_calls(self.session, start, end)
        except Exception:
            self.fail('fill_simple_calls failed with no data')

    def test_with_specific_range(self):
        start = t(2020, 1, 1)
        end = t(2020, 1, 31, 23, 59, 59, 999999)

        stat_dao.fill_simple_calls(self.session, start, end)

        result = self.session.query(StatCallOnQueue).all()
        assert_that(result, contains_exactly(has_properties(status='full')))

    def test_with_specific_timezone(self):
        # Asia/Shanghai is +08
        start = t(2020, 1, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai'))
        end = t(2020, 1, 31, 23, 59, 59, 999999)

        stat_dao.fill_simple_calls(self.session, start, end)

        result = self.session.query(StatCallOnQueue).all()
        assert_that(result, contains_exactly(has_properties(status='full')))

    def _create_functions(self):
        # WARNING: This functions should always be the same as the one in xivo-manage-db
        fill_simple_calls_fn = (
            pathlib.Path(__file__)
            .parent.joinpath('helpers/fill_simple_calls.sql')
            .read_text()
        )
        self.session.execute(text(fill_simple_calls_fn))


class TestFillLeaveEmptyCall(DAOTestCase):
    def setUp(self):
        DAOTestCase.setUp(self)
        self._create_functions()
        self.callid_found = '1404377805.6457'
        event = QueueLog(
            time=t(2020, 1, 1, 0, 0, 1, tzinfo=pytz.UTC),
            callid=self.callid_found,
            queuename='found_queue',
            event='LEAVEEMPTY',
        )
        self.add_me(event)
        event = QueueLog(
            time=t(2020, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
            callid=self.callid_found,
            queuename='found_queue',
            event='ENTERQUEUE',
        )
        self.add_me(event)
        queue = StatQueue(name='found_queue', tenant_uuid=self.default_tenant.uuid)
        self.add_me(queue)

        self.callid_ignored = '1000000000.0000'
        event = QueueLog(
            time=t(2020, 2, 1, tzinfo=pytz.UTC),
            callid=self.callid_ignored,
            queuename='ignored_queue',
            event='LEAVEEMPTY',
        )
        self.add_me(event)
        event = QueueLog(
            time=t(2020, 2, 1, tzinfo=pytz.UTC),
            callid=self.callid_ignored,
            queuename='ignored_queue',
            event='ENTERQUEUE',
        )
        self.add_me(event)
        queue = StatQueue(name='ignored_queue', tenant_uuid=self.default_tenant.uuid)
        self.add_me(queue)

    def test_empty(self):
        start = t(1999, 1, 1)
        end = t(1999, 1, 31, 23, 59, 59, 999999)
        try:
            stat_dao.fill_leaveempty_calls(self.session, start, end)
        except Exception:
            self.fail('fill_simple_calls failed with no data')

    def test_with_specific_range(self):
        start = t(2019, 1, 1)
        end = t(2020, 1, 31, 23, 59, 59, 999999)

        stat_dao.fill_leaveempty_calls(self.session, start, end)

        result = self.session.query(StatCallOnQueue).all()
        assert_that(result, contains_exactly(has_properties(callid=self.callid_found)))

    def test_with_specific_timezone(self):
        # Asia/Shanghai is +08
        start = t(2020, 1, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai'))
        end = t(2020, 1, 31, 23, 59, 59, 999999)

        stat_dao.fill_leaveempty_calls(self.session, start, end)

        result = self.session.query(StatCallOnQueue).all()
        assert_that(result, contains_exactly(has_properties(callid=self.callid_found)))

    def _create_functions(self):
        # WARNING: This functions should always be the same as the one in xivo-manage-db
        fill_leaveempty_calls_fn = (
            pathlib.Path(__file__)
            .parent.joinpath('helpers/fill_leaveempty_calls.sql')
            .read_text()
        )
        self.session.execute(text(fill_leaveempty_calls_fn))


class TestStatDAO(DAOTestCase):
    def setUp(self):
        DAOTestCase.setUp(self)
        self.start = t(2012, 7, 1, tzinfo=pytz.UTC)
        self.end = t(2012, 7, 31, 23, 59, 59, 999999, tzinfo=pytz.UTC)
        self.qname1, self.qid1 = self._insert_queue('q1')
        self.qname2, self.qid2 = self._insert_queue('q2')
        self.aname1, self.aid1 = self._insert_agent('a1')
        self.aname2, self.aid2 = self._insert_agent('a2')

    @staticmethod
    def _get_expected_call(call_list, callid):
        return [c for c in call_list if c[1] == callid][0]

    def test_get_login_intervals_in_range_calls_empty(self):
        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        assert len(result) == 0

    def test_get_login_intervals_when_login_same_as_start_no_logoff(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        logins = [
            {
                'time': self.start,
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
            }
        ]

        self._insert_agent_callback_logins_logoffs(logins, [])

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {self.aid1: sorted([(logins[0]['time'], self.end)])}

        assert expected == result

    def test_get_login_intervals_when_logoff_same_as_start_no_login(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        talktime = datetime.timedelta(minutes=1)

        logoffs = [
            {
                'time': self.start,
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            }
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        assert len(result) == 0

    def test_get_login_intervals_when_logoff_after_end_no_login(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        talktime = datetime.timedelta(minutes=1)
        logintime = self.end + datetime.timedelta(minutes=1)
        logouttime = logintime + talktime

        logoffs = [
            {
                'time': logouttime,
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        assert len(result) == 0

    def test_get_login_intervals_when_login_after_range(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        talktime = datetime.timedelta(minutes=1)
        logintime = self.start
        logouttime = logintime + talktime

        logins = [
            {
                'time': logintime,
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
            {
                'time': self.end + datetime.timedelta(minutes=1),
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
        ]

        logoffs = [
            {
                'time': logouttime,
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
        ]

        self._insert_agent_callback_logins_logoffs(logins, logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {self.aid1: sorted([(logintime, logouttime)])}

        assert expected == result

    def test_get_login_intervals_when_login_after_range_no_logoff(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        talktime = datetime.timedelta(minutes=1)

        logins = [
            {
                'time': self.end + datetime.timedelta(minutes=1),
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
        ]

        logoffs = []

        self._insert_agent_callback_logins_logoffs(logins, logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        assert len(result) == 0

    def test_get_login_intervals_when_logoff_same_as_end_no_login(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        talktime = datetime.timedelta(minutes=1)
        logintime = self.end - talktime
        logouttime = self.end

        logoffs = [
            {
                'time': logouttime,
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
                'talktime': talktime,
            },
        ]

        self._insert_agent_callback_logins_logoffs([], logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {self.aid1: sorted([(logintime, logouttime)])}

        assert expected == result

    def test_get_login_intervals_in_range_calls_logins_in_range(self):
        context = self.add_context()
        extension_1 = self.add_extension(context=context.name)
        extension_2 = self.add_extension(context=context.name)

        logintimes = [
            datetime.timedelta(minutes=10, seconds=13),
            datetime.timedelta(minutes=20),
            datetime.timedelta(minutes=7, seconds=21),
            datetime.timedelta(hours=2, minutes=3),
        ]

        cb_logins = [
            {
                'time': self.start + datetime.timedelta(seconds=30),
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension_1,
                'context': context,
            },
            {
                'time': self.start + datetime.timedelta(minutes=20),
                'callid': 'login_2',
                'agent': self.aname1,
                'extension': extension_2,
                'context': context,
            },
        ]

        cb_logoffs = [
            {
                'time': cb_logins[0]['time'] + logintimes[0],
                'callid': 'NONE',
                'agent': self.aname1,
                'extension': extension_1,
                'context': context,
                'talktime': logintimes[0],
            },
            {
                'time': cb_logins[1]['time'] + logintimes[1],
                'callid': 'NONE',
                'agent': self.aname1,
                'extension': extension_2,
                'context': context,
                'talktime': logintimes[1],
            },
        ]

        self._insert_agent_callback_logins_logoffs(cb_logins, cb_logoffs)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {
            self.aid1: sorted(
                [
                    (cb_logins[0]['time'], cb_logoffs[0]['time']),
                    (cb_logins[1]['time'], cb_logoffs[1]['time']),
                ]
            ),
        }

        assert expected == result

    def test_get_login_intervals_in_range_logins_before_no_logout(self):
        context = self.add_context()
        extension = self.add_extension(context=context.name)

        cb_logins = [
            {
                'time': self.start - datetime.timedelta(seconds=30),
                'callid': 'login_1',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
            },
            {
                'time': self.start - datetime.timedelta(seconds=44),
                'callid': 'login_5',
                'agent': self.aname1,
                'extension': extension,
                'context': context,
            },
        ]

        self._insert_agent_callback_logins_logoffs(cb_logins, [])

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {
            self.aid1: [(self.start, self.end)],
        }

        assert expected == result

    def test_get_login_intervals_in_range_no_login_logout_calls(self):
        connect1 = QueueLog(
            time=self.start - datetime.timedelta(minutes=5),
            callid='answered_1',
            queuename='queue',
            agent=self.aname1,
            event='CONNECT',
            data1='6',
            data2='linked_callid',
            data3='2',
        )
        self.add_me(connect1)
        connect2 = QueueLog(
            time=self.start + datetime.timedelta(minutes=5),
            callid='answered_2',
            queuename='queue',
            agent=self.aname2,
            event='CONNECT',
            data1='6',
            data2='linked_callid_2',
            data3='4',
        )

        self.add_me(connect2)

        result = stat_dao.get_login_intervals_in_range(
            self.session, self.start, self.end
        )

        expected = {}

        assert expected == result

    def _insert_agent_callback_logins_logoffs(self, logins, logoffs):
        with flush_session(self.session):
            for login in logins:
                callback_login = QueueLog(
                    time=login['time'],
                    callid=login['callid'],
                    queuename='NONE',
                    agent=login['agent'],
                    event='AGENTCALLBACKLOGIN',
                    data1=f'{login["extension"].exten}@{login["context"].name}',
                )
                self.session.add(callback_login)

            for logoff in logoffs:
                callback_logoff = QueueLog(
                    time=logoff['time'],
                    callid='NONE',
                    queuename='NONE',
                    agent=logoff['agent'],
                    event='AGENTCALLBACKLOGOFF',
                    data1=f'{logoff["extension"].exten}@{logoff["context"].name}',
                    data2=logoff['talktime'].seconds,
                )
                self.session.add(callback_logoff)

    def _insert_transferred_calls(self, transferred_calls):
        map(
            lambda transferred_call: self._insert_transferred_call(*transferred_call),
            transferred_calls,
        )

    def _insert_closed_calls(self, closed_calls):
        map(lambda closed_call: self._insert_closed_call(*closed_call), closed_calls)

    def _insert_completed_calls(self, completed_calls):
        map(
            lambda completed_call: self._insert_completed_call(*completed_call),
            completed_calls,
        )

    def _insert_full_calls(self, full_calls):
        map(lambda full_call: self._insert_full_call(*full_call), full_calls)

    def _insert_joinempty_calls(self, je_calls):
        map(lambda je_call: self._insert_joinempty_call(*je_call), je_calls)

    def _insert_leaveempty_calls(self, le_calls):
        map(lambda le_call: self._insert_leaveempty_call(*le_call), le_calls)

    def _insert_ca_ratio_calls(self, ca_ratio_calls):
        map(
            lambda ca_ratio_call: self._insert_ca_ratio_call(*ca_ratio_call),
            ca_ratio_calls,
        )

    def _insert_holdtime_calls(self, holdtime_calls):
        map(
            lambda holdtime_call: self._insert_holdtime_call(*holdtime_call),
            holdtime_calls,
        )

    def _insert_transferred_call(self, time, callid, qname, aname, waittime, talktime):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1',
        )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(
                TIMESTAMP_FORMAT
            ),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1',
        )

        transfer = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(
                TIMESTAMP_FORMAT
            ),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='TRANSFER',
            data1='s',
            data2='user',
            data3=str(waittime),
            data4=str(talktime),
        )

        self.add_me_all([enterqueue, connect, transfer])

    def _insert_completed_call(
        self, time, callid, qname, aname, waittime, talktime, agent_complete
    ):
        enterqueue = QueueLog(
            time=time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1001',
            data3='1',
        )

        connect = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime)).strftime(
                TIMESTAMP_FORMAT
            ),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='CONNECT',
            data1=str(waittime),
            data2='1344965966.141',
            data3='1',
        )

        complete = QueueLog(
            time=(time + datetime.timedelta(seconds=waittime + talktime)).strftime(
                TIMESTAMP_FORMAT
            ),
            callid=callid,
            queuename=qname,
            agent=aname,
            event='COMPLETEAGENT' if agent_complete else 'COMPLETECALLER',
            data1=str(waittime),
            data2=str(talktime),
        )

        self.add_me_all([enterqueue, connect, complete])

    def _insert_full_call(self, t, callid, qname):
        full = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='FULL',
        )

        self.add_me(full)

    def _insert_joinempty_call(self, t, callid, qname):
        je = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='JOINEMPTY',
        )

        self.session.add_me(je)

    def _insert_leaveempty_call(self, t, callid, qname, waittime):
        enterqueue = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='ENTERQUEUE',
            data2='1000',
            data3='1',
        )

        leave_time = t + datetime.timedelta(seconds=waittime)
        le = QueueLog(
            time=leave_time.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='LEAVEEMPTY',
        )

        self.add_me_all([enterqueue, le])

    def _insert_closed_call(self, t, callid, qname):
        closed = QueueLog(
            time=t.strftime(TIMESTAMP_FORMAT),
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='CLOSED',
        )

        self.add_me(closed)

    def _insert_ca_ratio_call(self, t, callid, qname):
        call = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='DIVERT_CA_RATIO',
        )

        self.add_me(call)

    def _insert_holdtime_call(self, t, callid, qname):
        call = QueueLog(
            time=t,
            callid=callid,
            queuename=qname,
            agent='NONE',
            event='DIVERT_HOLDTIME',
        )

        self.add_me(call)

    def _insert_agent(self, aname, tenant_uuid=None):
        tenant_uuid = tenant_uuid or self.default_tenant.uuid
        a = StatAgent(name=aname, tenant_uuid=tenant_uuid)

        self.add_me(a)

        return a.name, a.id

    def _insert_queue(self, qname, tenant_uuid=None):
        tenant_uuid = tenant_uuid or self.default_tenant.uuid
        q = StatQueue(name=qname, tenant_uuid=tenant_uuid)

        self.add_me(q)

        return q.name, q.id

    def test_merge_agent_statistics(self):
        stat_1 = {1: [(1, 2), (2, 3)]}
        stat_2 = {1: [(4, 5)]}
        stat_3 = {1: [(6, 7)]}
        stat_4 = {1: [(5, 8)]}

        statistics = stat_dao._merge_agent_statistics(stat_1, stat_2, stat_3, stat_4)

        expected = {1: [(1, 2), (2, 3), (4, 5), (5, 8)]}

        assert len(statistics) == len(expected)

        for agent, statistic in statistics.items():
            for login in statistic:
                self.assertTrue(login in expected[agent])

        for agent, statistic in expected.items():
            for login in statistic:
                self.assertTrue(login in statistics[agent])

    def test_filter_overlap(self):
        items = [(1, 2), (2, 3)]
        result = stat_dao._filter_overlap(items)

        assert sorted(result) == sorted(items)

        items = [(1, 2), (2, 3), (2, 4)]
        expected = [(1, 2), (2, 4)]
        result = stat_dao._filter_overlap(items)

        assert sorted(result) == sorted(expected)

        items = [(1, 2), (2, 4), (3, 4)]
        expected = [(1, 2), (2, 4)]
        result = stat_dao._filter_overlap(items)

        assert sorted(result) == sorted(expected)
