# -*- coding: utf-8 -*-

# Copyright (C) 2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


from mock import patch
from xivo_dao import queue_member_dao
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueMemberDAO(DAOTestCase):

    tables = [QueueMember]

    def setUp(self):
        self.empty_tables()

    @patch('xivo_dao.helpers.queuemember_formatter.format_queuemembers')
    def test_get_queuemembers(self, mock_format_queuemembers):
        with patch.object(self.session, 'query') as mock_query:
            old_queuemember_formatter = mock_format_queuemembers

            queue_member_dao.get_queuemembers()

            try:
                mock_query.assert_called_with(QueueMember)
                self.assertTrue(mock_format_queuemembers.called)
            finally:
                mock_format_queuemembers = old_queuemember_formatter

    def test_get_queue_members_for_queues(self):
        self._insert_queue_member('queue1', 'Agent/2', True)
        self._insert_queue_member('group1', 'SIP/abcdef', False)

        queue_members = queue_member_dao.get_queue_members_for_queues()

        self.assertEqual(len(queue_members), 1)

        queue_member = queue_members[0]
        self.assertEqual(queue_member.queue_name, 'queue1')
        self.assertEqual(queue_member.member_name, 'Agent/2')

    def _insert_queue_member(self, queue_name, member_name, is_queue):
        queue_member = QueueMember()
        queue_member.queue_name = queue_name
        queue_member.interface = member_name
        queue_member.penalty = 0
        queue_member.usertype = 'user'
        queue_member.userid = 1
        queue_member.channel = 'foobar'
        queue_member.category = 'queue' if is_queue else 'group'

        try:
            self.session.add(queue_member)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
