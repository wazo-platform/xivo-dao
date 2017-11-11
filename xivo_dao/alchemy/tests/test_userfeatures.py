# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      equal_to,
                      has_key,
                      has_properties,
                      is_not,
                      not_,
                      none)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests.test_dao import DAOTestCase


class TestAgent(DAOTestCase):

    def test_getter(self):
        agent = self.add_agent()
        user = self.add_user(agent_id=agent.id)

        assert_that(user.agent, equal_to(agent))


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

    def test_creator(self):
        user = self.add_user()
        line1 = self.add_line()
        line2 = self.add_line()
        user.lines = [line2, line1]
        self.session.flush()

        assert_that(user.user_lines, contains(
            has_properties(line_id=line2.id,
                           main_line=True),
            has_properties(line_id=line1.id,
                           main_line=False)
        ))
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


class TestSchedules(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        schedule = self.add_schedule()
        self.add_schedule_path(path='user', pathid=user.id, schedule_id=schedule.id)

        row = self.session.query(UserFeatures).filter_by(uuid=user.uuid).first()
        assert_that(row, equal_to(user))
        assert_that(row.schedules, contains(schedule))

    def test_setter(self):
        user = self.add_user()
        schedule1 = Schedule()
        schedule2 = Schedule()
        user.schedules = [schedule1, schedule2]

        row = self.session.query(UserFeatures).filter_by(uuid=user.uuid).first()
        assert_that(row, equal_to(user))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        user = self.add_user()
        schedule1 = Schedule()
        schedule2 = Schedule()
        user.schedules = [schedule1, schedule2]
        self.session.flush()

        user.schedules = []

        row = self.session.query(UserFeatures).filter_by(uuid=user.uuid).first()
        assert_that(row, equal_to(user))
        assert_that(row.schedules, empty())

        row = self.session.query(Schedule).first()
        assert_that(row, not_(none()))

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())


class TestDelete(DAOTestCase):

    def test_schedule_paths_are_deleted(self):
        user = self.add_user()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='user', pathid=user.id)

        self.session.delete(schedule)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())

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

    def test_ivr_dialactions_are_deleted(self):
        user = self.add_user()
        self.add_dialaction(category='ivr_choice', action='user', actionarg1=user.id)
        self.add_dialaction(category='ivr', action='user', actionarg1=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
