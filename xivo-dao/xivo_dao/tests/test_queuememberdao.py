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


import unittest

from mock import Mock, call, ANY
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.base import Base
from xivo_dao.queuememberdao import QueueMemberDAO
from xivo_dao.helpers.queuemember_formatter import QueueMemberFormatter


class TestQueueMemberDAO(unittest.TestCase):

    def test_get_queuemembers(self):
        session = Mock()
        queuemember_dao = QueueMemberDAO(session)
        old_queuemember_formatter = QueueMemberFormatter.format_queuemembers
        QueueMemberFormatter.format_queuemembers = Mock()
        expected_session_calls = [call.query(ANY)]
        expected_formatter_calls = [call.QueueMemberFormatter.format_queuemember]

        result = queuemember_dao.get_queuemembers()

        try:
            self.assertEqual(session.method_calls, expected_session_calls)
            self.assertTrue(QueueMemberFormatter.format_queuemembers.called)
        finally:
            QueueMemberFormatter.format_queuemembers = old_queuemember_formatter
