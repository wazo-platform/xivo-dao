# -*- coding: UTF-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from datetime import datetime, timedelta
from xivo_dao.alchemy.cel import CEL
from xivo_dao.helpers.cel_exception import CELException
from xivo_dao.helpers.cel_channel import CELChannel


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

    def test_is_caller_true(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', uniqueid=u'1', linkedid=u'1'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        cel_channel = CELChannel(cel_events)

        self.assertTrue(cel_channel.is_caller())

    def test_is_caller_false(self):
        cel_events = [
            _new_cel(eventtype='CHAN_START', uniqueid=u'2', linkedid=u'1'),
            _new_cel(eventtype='HANGUP'),
            _new_cel(eventtype='CHAN_END')
        ]

        cel_channel = CELChannel(cel_events)

        self.assertFalse(cel_channel.is_caller())
