# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime, timedelta
from xivo_dao.alchemy.dbconnection import DBConnection
from xivo_dao.alchemy.base import Base
from xivo_dao.alchemy.cel import CEL
from xivo_dao.celdao import CELDAO, CELChannel, CELException


def _new_datetime_generator(step=timedelta(seconds=1)):
    base_datetime = datetime.now()
    cur_datetime = base_datetime
    while True:
        yield cur_datetime
        cur_datetime = cur_datetime + step


def _new_incr_datetime_generator(step=timedelta(seconds=1), incr=timedelta(seconds=1)):
    base_datetime = datetime.now()
    cur_datetime = base_datetime
    cur_step = step
    while True:
        yield cur_datetime
        cur_datetime = cur_datetime + cur_step
        cur_step = cur_step + incr


def _new_cel(**kwargs):
    cel_kwargs = {
        'eventtype': '',
        'eventtime': datetime.now(),
        'userdeftype': '',
        'cid_name': u'name1',
        'cid_num': u'num1',
        'cid_ani': '',
        'cid_rdnis': '',
        'cid_dnid': '',
        'exten': u'1',
        'context': 'default',
        'channame': u'SIP/A',
        'appname': '',
        'appdata': '',
        'amaflags': 3,
        'accountcode': '',
        'peeraccount': '',
        'uniqueid': '1',
        'linkedid': '1',
        'userfield': '',
        'peer': '',
    }
    cel_kwargs.update(kwargs)
    return CEL(**cel_kwargs)


class TestCELChannel(unittest.TestCase):
    def setUp(self):
        self._datetime_gen = _new_datetime_generator()

    def test_missing_chan_start_event(self):
        cel_events = [
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        self.assertRaises(CELException, CELChannel, cel_events)

    def test_missing_hangup_event(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='CHAN_END')
        ]

        self.assertRaises(CELException, CELChannel, cel_events)

    def test_missing_chan_end_event(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='HANGUP')
        ]

        self.assertRaises(CELException, CELChannel, cel_events)

    def test_channel_start_time(self):
        datetime_gen = _new_datetime_generator()
        start_time = datetime_gen.next()
        cel_events = [
            _new_cel(eventtype='CHAN_START', eventtime=start_time),
            _new_cel(eventtype='HANGUP', eventtime=datetime_gen.next()),
            _new_cel(eventtype='CHAN_END', eventtime=datetime_gen.next())
        ]

        channel = CELChannel(cel_events)
        self.assertEqual(start_time, channel.channel_start_time())

    def test_channel_is_answered_when_answered(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='ANSWER'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertTrue(channel.is_answered())

    def test_channel_is_not_answered_when_not_answered(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertFalse(channel.is_answered())

    def test_answer_duration_zero_when_not_answered(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertEqual(0.0, channel.answer_duration())

    def test_answer_duration_when_answered(self):
        datetime_gen = _new_incr_datetime_generator()
        cel_events = [
            _new_cel(eventtype='CHAN_START', eventtime=datetime_gen.next()),
            _new_cel(eventtype='ANSWER', eventtime=datetime_gen.next()),
            _new_cel(eventtype='HANGUP', eventtime=datetime_gen.next()),
            _new_cel(eventtype='CHAN_END', eventtime=datetime_gen.next())
        ]

        channel = CELChannel(cel_events)
        self.assertEqual(2.0, channel.answer_duration())

    def test_exten_when_not_from_originate(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', exten=u'100'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertEqual(u'100', channel.exten())

    def test_exten_when_from_originate(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', exten=u's'),
            _new_cel(eventtype='ANSWER', cid_name=u'100'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertEqual(u'100', channel.exten())

    def test_linked_id(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', linkedid='2'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        channel = CELChannel(cel_events)
        self.assertEqual('2', channel.linked_id())

    def test_linkedid_end_event_is_present(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END'),
            _new_cel(eventtype='LINKEDID_END')
        ]

        CELChannel(cel_events)

    def test_is_originate(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', uniqueid=1, exten=u's'),
            _new_cel(eventtype='ANSWER', uniqueid=1),
            _new_cel(eventtype='APP_START', uniqueid=1),
            _new_cel(eventtype='CHAN_START', uniqueid=2),
            _new_cel(eventtype='ANSWER', uniqueid=2),
            _new_cel(eventtype='BRIDGE_START', uniqueid=1),
            _new_cel(eventtype='BRIDGE_END', uniqueid=1),
            _new_cel(eventtype='HANGUP', uniqueid=2),
            _new_cel(eventtype='CHAN_END', uniqueid=2),
            _new_cel(eventtype='HANGUP', uniqueid=1),
            _new_cel(eventtype='CHAN_END', uniqueid=1),
        ]

        cel_channel = CELChannel(cel_events)

        self.assertTrue(cel_channel.is_originate())

        cel_events = [
            _new_cel(eventtype='CHAN_START', uniqueid=1),
            _new_cel(eventtype='ANSWER', uniqueid=1),
            _new_cel(eventtype='APP_START', uniqueid=1),
            _new_cel(eventtype='CHAN_START', uniqueid=2),
            _new_cel(eventtype='ANSWER', uniqueid=2),
            _new_cel(eventtype='BRIDGE_START', uniqueid=1),
            _new_cel(eventtype='BRIDGE_END', uniqueid=1),
            _new_cel(eventtype='HANGUP', uniqueid=2),
            _new_cel(eventtype='CHAN_END', uniqueid=2),
            _new_cel(eventtype='HANGUP', uniqueid=1),
            _new_cel(eventtype='CHAN_END', uniqueid=1),
        ]

        cel_channel = CELChannel(cel_events)

        self.assertFalse(cel_channel.is_originate())


class TestCELDAO(unittest.TestCase):
    _URI = 'sqlite:///:memory:'

    def setUp(self):
        self._connection = DBConnection(self._URI)
        self._connection.connect()
        self._session = self._connection.get_session()
        self._celdao = CELDAO(self._session)

        Base.metadata.create_all(self._connection.get_engine(), [CEL.__table__])

        self._datetime_gen = _new_datetime_generator()

    def tearDown(self):
        Base.metadata.drop_all(self._connection.get_engine(), [CEL.__table__])

        self._connection.close()

    def _insert_cels(self, cels):
        for cel in cels:
            self._session.add(cel)
        self._session.commit()

    def test_caller_id_by_unique_id_when_unique_id_is_present(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', cid_name='name1', cid_num='num1',
                     uniqueid='1'),
            _new_cel(eventtype='CHAN_START', cid_name='name2', cid_num='num2',
                     uniqueid='2'),
        ])

        self.assertEqual('"name2" <num2>', self._celdao.caller_id_by_unique_id('2'))

    def test_caller_id_by_unique_id_when_unique_id_is_missing(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', cid_name='name1', cid_num='num1',
                     uniqueid='1'),
        ])

        self.assertRaises(CELException, self._celdao.caller_id_by_unique_id, '2')

    def test_channel_by_unique_id_when_channel_is_present(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', uniqueid='1', exten=u'100'),
            _new_cel(eventtype='HANGUP', uniqueid='1'),
            _new_cel(eventtype='CHAN_END', uniqueid='1'),
        ])

        channel = self._celdao.channel_by_unique_id('1')
        self.assertEqual(u'100', channel.exten())

    def test_channels_by_linked_id(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', uniqueid='1', linkedid='67', exten=u's'),
            _new_cel(eventtype='ANSWER', uniqueid='1', linkedid='67'),
            _new_cel(eventtype='APP_START', uniqueid='1', linkedid='67'),
            _new_cel(eventtype='CHAN_START', uniqueid='2', linkedid='67'),
            _new_cel(eventtype='ANSWER', uniqueid='2', linkedid='67'),
            _new_cel(eventtype='BRIDGE_START', uniqueid='1', linkedid='67'),
            _new_cel(eventtype='BRIDGE_END', uniqueid='1', linkedid='67'),
            _new_cel(eventtype='HANGUP', uniqueid='2', linkedid='67'),
            _new_cel(eventtype='CHAN_END', uniqueid='2', linkedid='67'),
            _new_cel(eventtype='HANGUP', uniqueid='1', linkedid='67'),
            _new_cel(eventtype='CHAN_END', uniqueid='1', linkedid='67'),
        ])

        cels = self._celdao.cels_by_linked_id(67)

        channel_ids = set()

        for cel in cels:
            channel_ids.add(cel.uniqueid)

        self.assertTrue('1' in channel_ids)
        self.assertTrue('2' in channel_ids)

    def test_channel_by_unique_id_when_channel_is_missing(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', uniqueid='2'),
            _new_cel(eventtype='HANGUP', uniqueid='2'),
            _new_cel(eventtype='CHAN_END', uniqueid='2'),
        ])

        self.assertRaises(CELException, self._celdao.channel_by_unique_id, '1')

    def test_1_answered_call_to_dialplan(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0')
        ])

        answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(answered_channels))

        missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(missed_channels))

        outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(outgoing_channels))
        outgoing_channel = outgoing_channels[0]
        self.assertTrue(outgoing_channel.is_answered())

    def test_1_unanswered_call_to_dialplan(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0')
        ])

        answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(answered_channels))

        missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(missed_channels))

        outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(outgoing_channels))
        outgoing_channel = outgoing_channels[0]
        self.assertFalse(outgoing_channel.is_answered())

    def test_1_answered_call_to_phone(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0', uniqueid='1')
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(a_outgoing_channels))
        a_outgoing_channel = a_outgoing_channels[0]
        self.assertTrue(a_outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_answered_channels))
        b_answered_channel = b_answered_channels[0]
        self.assertTrue(b_answered_channel.is_answered())

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_missed_channels))

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

    def test_1_unanswered_call_to_phone_but_answered_by_dialplan(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0', uniqueid='1')
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(a_outgoing_channels))
        outgoing_channel = a_outgoing_channels[0]
        self.assertTrue(outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_answered_channels))

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_missed_channels))
        b_missed_channel = b_missed_channels[0]
        self.assertFalse(b_missed_channel.is_answered())

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

    def test_1_unanswered_call_to_phone_and_unanswered_by_dialplan(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0', uniqueid='1')
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(a_outgoing_channels))
        outgoing_channel = a_outgoing_channels[0]
        self.assertFalse(outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_answered_channels))

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_missed_channels))
        b_missed_channel = b_missed_channels[0]
        self.assertFalse(b_missed_channel.is_answered())

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

    def test_1_answered_but_in_progress_call_to_phone(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0', uniqueid='1'),
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_outgoing_channels))

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_answered_channels))

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_missed_channels))

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

    def test_3_way_conference(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='ANSWER', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/A-1',
                     uniqueid='3', linkedid='3'),
            _new_cel(eventtype='CHAN_START', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='ANSWER', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-1',
                     uniqueid='3', linkedid='3'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='CHAN_END', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-1',
                     uniqueid='3', linkedid='3'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-1',
                     uniqueid='3', linkedid='3')
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(2, len(a_outgoing_channels))
        a1_outgoing_channel = a_outgoing_channels[0]
        a2_outgoing_channel = a_outgoing_channels[1]
        self.assertTrue(a1_outgoing_channel.is_answered())
        self.assertTrue(a2_outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_answered_channels))
        b_answered_channel = b_answered_channels[0]
        self.assertTrue(b_answered_channel.is_answered())

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_missed_channels))

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

        c_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(1, len(c_answered_channels))
        c_answered_channel = c_answered_channels[0]
        self.assertTrue(c_answered_channel.is_answered())

        c_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(0, len(c_missed_channels))

        c_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(0, len(c_outgoing_channels))

    def test_1_answered_call_to_phone_from_originate(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0', uniqueid='1',),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='APP_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='ANSWER', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='BRIDGE_START', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='BRIDGE_END', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0', uniqueid='2'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0', uniqueid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0', uniqueid='1')
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(1, len(a_outgoing_channels))
        a_outgoing_channel = a_outgoing_channels[0]
        self.assertTrue(a_outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_answered_channels))
        b_answered_channel = b_answered_channels[0]
        self.assertTrue(b_answered_channel.is_answered())

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_missed_channels))

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

    def test_1_call_to_phone_then_answered_attended_transfer(self):
        self._insert_cels([
            _new_cel(eventtype='CHAN_START', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='ANSWER', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_START', channame='SIP/A-1',
                     uniqueid='3', linkedid='3'),
            _new_cel(eventtype='CHAN_START', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='ANSWER', channame='SIP/C-0',
                     uniqueid='4', linkedid='3'),
            _new_cel(eventtype='ANSWER', channame='SIP/A-1',
                     uniqueid='3', linkedid='3'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-0',
                     uniqueid='1', linkedid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/A-1',
                     uniqueid='3', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/A-1',
                     uniqueid='3', linkedid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/B-0',
                     uniqueid='2', linkedid='1'),
            _new_cel(eventtype='HANGUP', channame='SIP/C-0',
                     uniqueid='4', linkedid='1'),
            _new_cel(eventtype='CHAN_END', channame='SIP/C-0',
                     uniqueid='4', linkedid='1'),
        ])

        a_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_answered_channels))

        a_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(0, len(a_missed_channels))

        a_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/A', 5)
        self.assertEqual(2, len(a_outgoing_channels))
        a1_outgoing_channel = a_outgoing_channels[0]
        a2_outgoing_channel = a_outgoing_channels[1]
        self.assertTrue(a1_outgoing_channel.is_answered())
        self.assertTrue(a2_outgoing_channel.is_answered())

        b_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(1, len(b_answered_channels))
        b_answered_channel = b_answered_channels[0]
        self.assertTrue(b_answered_channel.is_answered())

        b_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_missed_channels))

        b_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/B', 5)
        self.assertEqual(0, len(b_outgoing_channels))

        c_answered_channels = self._celdao.answered_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(1, len(c_answered_channels))
        c_answered_channel = c_answered_channels[0]
        self.assertTrue(c_answered_channel.is_answered())

        c_missed_channels = self._celdao.missed_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(0, len(c_missed_channels))

        c_outgoing_channels = self._celdao.outgoing_channels_for_endpoint('SIP/C', 5)
        self.assertEqual(0, len(c_outgoing_channels))
