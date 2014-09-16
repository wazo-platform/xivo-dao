# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import time

from hamcrest import assert_that
from hamcrest import equal_to
from sqlalchemy import and_
from xivo_dao.alchemy.queueinfo import QueueInfo
from xivo_dao import queue_info_dao
from xivo_dao.tests.test_dao import DAOTestCase


class TestQueueInfo(DAOTestCase):

    def test_add_entry(self):
        calltime, queue, calleridnum, uniqueid = int(time.time()), 'my_queue', 'cid', 'uniqueid123'

        queue_info_dao.add_entry(calltime, queue, calleridnum, uniqueid)

        last_entry = self.session.query(
            QueueInfo.call_time_t,
            QueueInfo.queue_name,
            QueueInfo.caller,
            QueueInfo.caller_uniqueid,
        ).order_by(QueueInfo.id).first()

        assert_that(last_entry.call_time_t, equal_to(calltime))
        assert_that(last_entry.queue_name, equal_to(queue))
        assert_that(last_entry.caller, equal_to(calleridnum))
        assert_that(last_entry.caller_uniqueid, equal_to(uniqueid))

    def test_update_holdtime(self):
        answerer, holdtime = 'answerer', 10

        qi = self.add_queue_info()

        queue_info_dao.update_holdtime(
            qi.caller_uniqueid, qi.call_time_t, holdtime, answerer)

        updated_qi = self.session.query(
            QueueInfo.call_picker, QueueInfo.hold_time
        ).filter(
            and_(QueueInfo.caller_uniqueid == qi.caller_uniqueid,
                 QueueInfo.call_time_t == qi.call_time_t)
        ).first()

        assert_that(updated_qi.call_picker, equal_to(answerer))
        assert_that(updated_qi.hold_time, equal_to(holdtime))

    def test_update_holdtime_no_answerer(self):
        answerer, holdtime = 'name', 42

        qi = self.add_queue_info(call_picker=answerer)

        queue_info_dao.update_holdtime(qi.caller_uniqueid, qi.call_time_t, holdtime)

        updated_qi = self.session.query(
            QueueInfo.hold_time,
            QueueInfo.call_picker,
        ).filter(
            and_(QueueInfo.caller_uniqueid == qi.caller_uniqueid,
                 QueueInfo.call_time_t == qi.call_time_t)
        ).first()

        assert_that(updated_qi.hold_time, equal_to(holdtime))
        assert_that(updated_qi.call_picker, equal_to(answerer))

    def test_update_talktime(self):
        talktime = 26

        qi = self.add_queue_info()

        queue_info_dao.update_talktime(qi.caller_uniqueid, qi.call_time_t, talktime)

        updated_qi = self.session.query(
            QueueInfo.talk_time,
        ).filter(
            and_(QueueInfo.caller_uniqueid == qi.caller_uniqueid,
                 QueueInfo.call_time_t == qi.call_time_t)
        ).first()

        assert_that(updated_qi.talk_time, equal_to(talktime))
