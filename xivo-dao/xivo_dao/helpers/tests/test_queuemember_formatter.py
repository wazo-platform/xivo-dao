# -*- coding: utf-8 -*-

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
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.base import Base

from xivo_dao.helpers.queuemember_formatter import QueueMemberFormatter


class TestQueueMemberFormatter(unittest.TestCase):

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [QueueMember.__table__])
        Base.metadata.create_all(connection.get_engine(), [QueueMember.__table__])

        self.session = connection.get_session()

        self._insert_data()
        self._define_expected()

        self.ami_event = {
            'Queue': 'queue1',
            'Location': 'agent1',
            'Status': 'status1',
            'Paused': 'yes',
            'Membership': 'dynamic',
            'CallsTaken': '0',
            'Penalty': '0',
            'LastCall': 'none'}
        self.ami_event_formatted = {'agent1,queue1': {
            'queue_name': 'queue1',
            'interface': 'agent1',
            'membership': 'dynamic',
            'penalty': '0',
            'status': 'status1',
            'paused': 'yes'}}

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def _insert_data(self):
        self.queuem1 = QueueMember()
        self.queuem1.queue_name = 'queue1'
        self.queuem1.interface = 'agent1'
        self.queuem1.penalty = 0
        self.queuem1.paused = 0
        self.queuem1.usertype = 'user'
        self.queuem1.userid = 1
        self.queuem1.channel = 'chan1'
        self.queuem1.category = 'queue'
        self.queuem2 = QueueMember()
        self.queuem2.queue_name = 'queue2'
        self.queuem2.interface = 'agent2'
        self.queuem2.penalty = 0
        self.queuem2.paused = 0
        self.queuem2.usertype = 'agent'
        self.queuem2.userid = 2
        self.queuem2.channel = 'chan2'
        self.queuem2.category = 'queue'
        self.queuem3 = QueueMember()
        self.queuem3.queue_name = 'queue3'
        self.queuem3.interface = 'agent3'
        self.queuem3.penalty = 0
        self.queuem3.paused = 0
        self.queuem3.usertype = 'user'
        self.queuem3.userid = 3
        self.queuem3.channel = 'chan3'
        self.queuem3.category = 'group'
        self.queuem4 = QueueMember()
        self.queuem4.queue_name = 'queue4'
        self.queuem4.interface = 'agent4'
        self.queuem4.penalty = 0
        self.queuem4.paused = 0
        self.queuem4.usertype = 'agent'
        self.queuem4.userid = 4
        self.queuem4.channel = 'chan4'
        self.queuem4.category = 'group'
        self.session.add(self.queuem1)
        self.session.add(self.queuem2)
        self.session.add(self.queuem3)
        self.session.add(self.queuem4)
        self.session.commit()

    def _define_expected(self):
        self.queuem1_dict = {
            'queue_name': u'queue1',
            'interface': u'agent1',
            'penalty': 0,
            'call_limit': 0,
            'paused': 0,
            'commented': 0,
            'usertype': 'user',
            'userid': 1,
            'channel': u'chan1',
            'category': 'queue',
            'skills': u'',
            'state_interface': u''
        }
        self.queuem2_dict = {
            'queue_name': u'queue2',
            'interface': u'agent2',
            'penalty': 0,
            'call_limit': 0,
            'paused': 0,
            'commented': 0,
            'usertype': 'agent',
            'userid': 2,
            'channel': u'chan2',
            'category': 'queue',
            'skills': u'',
            'state_interface': u''
        }
        self.queuem3_dict = {
            'queue_name': u'queue3',
            'interface': u'agent3',
            'penalty': 0,
            'call_limit': 0,
            'paused': 0,
            'commented': 0,
            'usertype': 'user',
            'userid': 3,
            'channel': u'chan3',
            'category': 'group',
            'skills': u'',
            'state_interface': u''
        }
        self.queuem4_dict = {
            'queue_name': u'queue4',
            'interface': u'agent4',
            'penalty': 0,
            'call_limit': 0,
            'paused': 0,
            'commented': 0,
            'usertype': 'agent',
            'userid': 4,
            'channel': u'chan4',
            'category': 'group',
            'skills': u'',
            'state_interface': u''
        }

    def test_format_queuemembers(self):
        query_result = self.session.query(QueueMember)
        expected_result = {
            'agent1,queue1': self.queuem1_dict,
            'agent2,queue2': self.queuem2_dict,
            'agent3,queue3': self.queuem3_dict,
            'agent4,queue4': self.queuem4_dict
        }
        result = QueueMemberFormatter.format_queuemembers(query_result)

        self.assertEqual(result, expected_result)

    def test_generate_key(self):
        queuemember = self.queuem1_dict
        expected_result = 'agent1,queue1'

        result = QueueMemberFormatter._generate_key(queuemember)

        self.assertEqual(result, expected_result)

    def test_convert_row_to_dict(self):
        query_result = self.session.query(QueueMember).filter(QueueMember.queue_name == 'queue1')
        row = query_result[0]
        expected_result = self.queuem1_dict

        result = QueueMemberFormatter._convert_row_to_dict(row)

        self.assertEqual(result, expected_result)

    def test_format_queuemember_from_ami_add(self):
        ami_event = self.ami_event
        expected_result = self.ami_event_formatted

        result = QueueMemberFormatter.format_queuemember_from_ami_add(ami_event)

        self.assertEqual(result, expected_result)

    def test_format_queuemember_from_ami_remove(self):
        ami_event = self.ami_event
        expected_result = {'agent1,queue1': {
                'queue_name': 'queue1',
                'interface': 'agent1'}}

        result = QueueMemberFormatter.format_queuemember_from_ami_remove(ami_event)

        self.assertEqual(result, expected_result)

    def test_format_queuemember_from_ami_update(self):
        ami_event = self.ami_event
        expected_result = self.ami_event_formatted

        result = QueueMemberFormatter.format_queuemember_from_ami_update(ami_event)

        self.assertEqual(result, expected_result)

    def test_format_queuemember_from_ami_pause(self):
        ami_event = {'Queue': 'queue1',
                     'Location': 'agent1',
                     'Paused': '0'}
        expected_result = {'agent1,queue1': {
                'queue_name': 'queue1',
                'interface': 'agent1',
                'paused': '0'}}

        result = QueueMemberFormatter.format_queuemember_from_ami_pause(ami_event)

        self.assertEqual(result, expected_result)

    def test_extract_ami(self):
        field_list = ['queue_name', 'interface', 'membership']
        ami_event = self.ami_event
        expected_result = {'agent1,queue1': {
            'queue_name': 'queue1',
            'interface': 'agent1',
            'membership': 'dynamic'}}

        result = QueueMemberFormatter._extract_ami(field_list, ami_event)

        self.assertEqual(result, expected_result)
