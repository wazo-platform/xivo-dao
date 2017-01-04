# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      equal_to,
                      has_key,
                      has_properties,
                      is_not,
                      none)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase


class TestFullname(DAOTestCase):

    def test_getter(self):
        user = UserFeatures()
        user.firstname = 'firstname'
        user.lastname = 'lastname'

        assert_that(user.fullname, equal_to('firstname lastname'))


class TestLines(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        line1 = self.add_line()
        line2 = self.add_line()
        self.add_user_line(user_id=user.id, line_id=line1.id, main_line=False)
        self.add_user_line(user_id=user.id, line_id=line2.id, main_line=True)

        assert_that(user.lines, contains(line2, line1))


class TestIncalls(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        incall1 = self.add_incall(destination=Dialaction(action='user', actionarg1=str(user.id)))
        incall2 = self.add_incall(destination=Dialaction(action='user', actionarg1=str(user.id)))

        assert_that(user.incalls, contains_inanyorder(incall1, incall2))


class TestGroups(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        group1 = self.add_group()
        group2 = self.add_group()
        self.add_queue_member(queue_name=group1.name, category='group', usertype='user', userid=user.id)
        self.add_queue_member(queue_name=group2.name, category='group', usertype='user', userid=user.id)

        assert_that(user.groups, contains_inanyorder(group1, group2))

    def test_getter_when_queuemember_has_queue(self):
        user = self.add_user()
        queue = self.add_queuefeatures()
        self.add_queue_member(queue_name=queue.name, category='queue', usertype='user', userid=user.id)

        assert_that(user.groups, empty())


class TestQueueMembers(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        qm1 = self.add_queue_member(category='queue', usertype='user', userid=user.id)
        qm2 = self.add_queue_member(category='queue', usertype='user', userid=user.id)

        assert_that(user.queue_members, contains_inanyorder(qm1, qm2))


class TestVoicemail(DAOTestCase):

    def test_getter(self):
        voicemail = self.add_voicemail()
        user = self.add_user(voicemail_id=voicemail.id)

        assert_that(user.voicemail, equal_to(voicemail))


class TestFallbacks(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        dialaction = self.add_dialaction(event='key',
                                         category='user',
                                         categoryval=str(user.id))

        assert_that(user.fallbacks['key'], equal_to(dialaction))

    def test_setter(self):
        user = self.add_user()
        dialaction = Dialaction(action='none')

        user.fallbacks = {'key': dialaction}
        self.session.flush()

        assert_that(user.fallbacks['key'], equal_to(dialaction))

    def test_setter_to_none(self):
        user = self.add_user()

        user.fallbacks = {'key': None}
        self.session.flush()

        assert_that(user.fallbacks, empty())

    def test_setter_existing_key(self):
        user = self.add_user()
        dialaction1 = Dialaction(action='none')

        user.fallbacks = {'key': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        user.fallbacks = {'key': dialaction2}
        self.session.flush()

        assert_that(user.fallbacks['key'], has_properties(action='user',
                                                          actionarg1='1'))

    def test_setter_delete_undefined_key(self):
        user = self.add_user()
        dialaction1 = Dialaction(action='none')

        user.fallbacks = {'noanswer': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        user.fallbacks = {'busy': dialaction2}
        self.session.flush()

        assert_that(user.fallbacks, is_not(has_key('noanswer')))


class TestDelete(DAOTestCase):

    def test_group_members_are_deleted(self):
        user = self.add_user()
        self.add_queue_member(category='group', usertype='user', userid=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())

    def test_queue_members_are_deleted(self):
        user = self.add_user()
        self.add_queue_member(category='queue', usertype='user', userid=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())

    def test_user_lines_are_deleted(self):
        user = self.add_user()
        line = self.add_line()
        self.add_user_line(user_id=user.id, line_id=line.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(UserLine).first()
        assert_that(row, none())

    def test_paging_users_are_deleted(self):
        user = self.add_user()
        paging = self.add_paging()
        self.add_paging_user(user_id=user.id, paging_id=paging.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(PagingUser).first()
        assert_that(row, none())
