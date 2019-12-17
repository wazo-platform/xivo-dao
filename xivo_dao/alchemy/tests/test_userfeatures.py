# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_key,
    has_properties,
    is_not,
    none,
    not_,
)

from xivo_dao.alchemy.callfiltermember import Callfiltermember as CallFilterMember
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.paginguser import PagingUser
from xivo_dao.alchemy.pickupmember import PickupMember as CallPickupMember
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember as CallPermissionAssociation
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


class TestCallFilterRecipients(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        call_filter1 = self.add_call_filter()
        call_filter2 = self.add_call_filter()
        recipient1 = self.add_call_filter_member(
            callfilterid=call_filter1.id,
            bstype='boss',
            type='user',
            typeval=str(user.id)
        )
        recipient2 = self.add_call_filter_member(
            callfilterid=call_filter2.id,
            bstype='boss',
            type='user',
            typeval=str(user.id)
        )

        assert_that(user.call_filter_recipients, contains_inanyorder(recipient1, recipient2))


class TestCallFilterSurrogates(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        call_filter1 = self.add_call_filter()
        call_filter2 = self.add_call_filter()
        surrogate1 = self.add_call_filter_member(
            callfilterid=call_filter1.id,
            bstype='secretary',
            type='user',
            typeval=str(user.id)
        )
        surrogate2 = self.add_call_filter_member(
            callfilterid=call_filter2.id,
            bstype='secretary',
            type='user',
            typeval=str(user.id)
        )

        assert_that(user.call_filter_surrogates, contains_inanyorder(surrogate1, surrogate2))


class TestCallPickupInterceptorPickups(DAOTestCase):
    def test_getter(self):
        user_interceptor = self.add_user()
        user_target = self.add_user()
        call_pickup = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='member',
            membertype='user',
            memberid=user_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='pickup',
            membertype='user',
            memberid=user_target.id,
        )

        assert_that(
            user_interceptor.call_pickup_interceptor_pickups, contains(call_pickup)
        )

    def test_one_pickup_two_user_targets(self):
        user_interceptor = self.add_user()
        user_target1 = self.add_user()
        user_target2 = self.add_user()
        call_pickup1 = self.add_pickup()

        call_pickup1.user_interceptors = [user_interceptor]
        call_pickup1.user_targets = [user_target1, user_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            user_interceptor.call_pickup_interceptor_pickups,
            contains(call_pickup1),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_user_targets,
            contains(contains(user_target1, user_target2)),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_targets,
            contains(empty()),
        )

    def test_two_pickups_two_user_targets(self):
        user_interceptor = self.add_user()
        user_target1 = self.add_user()
        user_target2 = self.add_user()

        call_pickup1 = self.add_pickup()
        call_pickup1.user_interceptors = [user_interceptor]
        call_pickup1.user_targets = [user_target1]

        call_pickup2 = self.add_pickup()
        call_pickup2.user_interceptors = [user_interceptor]
        call_pickup2.user_targets = [user_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            user_interceptor.call_pickup_interceptor_pickups,
            contains(call_pickup1, call_pickup2),
        )

        assert_that(
            user_interceptor.users_from_call_pickup_user_targets,
            contains(contains(user_target1), contains(user_target2)),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_targets,
            contains(empty(), empty()),
        )

    # Groups
    def test_one_pickup_one_group_target(self):
        user_interceptor = self.add_user()
        user_target = self.add_user()
        group_target = self.add_group()
        self.add_queue_member(
            queue_name=group_target.name,
            category='group',
            usertype='user',
            userid=user_target.id,
        )
        call_pickup = self.add_pickup()

        call_pickup.user_interceptors = [user_interceptor]
        call_pickup.group_targets = [group_target]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            user_interceptor.call_pickup_interceptor_pickups,
            contains(call_pickup),
        )

        assert_that(
            user_interceptor.users_from_call_pickup_user_targets,
            contains(empty()),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_targets,
            contains(contains(contains(user_target))),
        )

    def test_one_pickup_two_group_targets(self):
        user_interceptor = self.add_user()
        user_target1 = self.add_user()
        group_target1 = self.add_group()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        user_target2 = self.add_user()
        group_target2 = self.add_group()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup1 = self.add_pickup()

        call_pickup1.user_interceptors = [user_interceptor]
        call_pickup1.group_targets = [group_target1, group_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            user_interceptor.call_pickup_interceptor_pickups,
            contains(call_pickup1),
        )

        assert_that(
            user_interceptor.users_from_call_pickup_user_targets,
            contains(empty()),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_targets,
            contains(contains(contains(user_target1), contains(user_target2))),
        )

    def test_two_pickups_two_group_targets(self):
        user_interceptor = self.add_user()
        user_target1 = self.add_user()
        group_target1 = self.add_group()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        user_target2 = self.add_user()
        group_target2 = self.add_group()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup1 = self.add_pickup()
        call_pickup1.user_interceptors = [user_interceptor]
        call_pickup1.group_targets = [group_target1]

        call_pickup2 = self.add_pickup()
        call_pickup2.user_interceptors = [user_interceptor]
        call_pickup2.group_targets = [group_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            user_interceptor.call_pickup_interceptor_pickups,
            contains(call_pickup1, call_pickup2),
        )

        assert_that(
            user_interceptor.users_from_call_pickup_user_targets,
            contains(empty(), empty()),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_targets,
            contains(
                contains(contains(user_target1)),
                contains(contains(user_target2)),
            ),
        )


class TestUsersFromCallPickupGroupInterceptorsUserTargets(DAOTestCase):
    def test_one_pickup_two_user_targets(self):
        user_interceptor = self.add_user()
        group_interceptor = self.add_group()
        self.add_queue_member(
            queue_name=group_interceptor.name,
            category='group',
            usertype='user',
            userid=user_interceptor.id,
        )
        user_target1 = self.add_user()
        user_target2 = self.add_user()
        call_pickup = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='pickup',
            membertype='user',
            memberid=user_target1.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='pickup',
            membertype='user',
            memberid=user_target2.id,
        )

        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_user_targets,
            contains(contains(contains(user_target1, user_target2))),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_group_targets,
            contains(contains(empty())),
        )

    def test_two_pickups_two_user_targets(self):
        user_interceptor = self.add_user()
        group_interceptor = self.add_group()
        self.add_queue_member(
            queue_name=group_interceptor.name,
            category='group',
            usertype='user',
            userid=user_interceptor.id,
        )
        user_target1 = self.add_user()
        user_target2 = self.add_user()
        call_pickup1 = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup1.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup1.id,
            category='pickup',
            membertype='user',
            memberid=user_target1.id,
        )
        call_pickup2 = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup2.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup2.id,
            category='pickup',
            membertype='user',
            memberid=user_target2.id,
        )

        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_user_targets,
            contains(contains(contains(user_target1), contains(user_target2))),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_group_targets,
            contains(contains(empty(), empty())),
        )


class TestUsersFromCallPickupGroupInterceptorsGroupTargets(DAOTestCase):
    def test_one_pickup_two_user_targets(self):
        user_interceptor = self.add_user()
        group_interceptor = self.add_group()
        self.add_queue_member(
            queue_name=group_interceptor.name,
            category='group',
            usertype='user',
            userid=user_interceptor.id,
        )
        user_target1 = self.add_user()
        group_target1 = self.add_group()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        user_target2 = self.add_user()
        group_target2 = self.add_group()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='pickup',
            membertype='group',
            memberid=group_target1.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup.id,
            category='pickup',
            membertype='group',
            memberid=group_target2.id,
        )

        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_user_targets,
            contains(contains(empty())),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_group_targets,
            contains(contains(contains(contains(user_target1), contains(user_target2)))),
        )

    def test_two_pickups_two_user_targets(self):
        user_interceptor = self.add_user()
        group_interceptor = self.add_group()
        self.add_queue_member(
            queue_name=group_interceptor.name,
            category='group',
            usertype='user',
            userid=user_interceptor.id,
        )
        user_target1 = self.add_user()
        group_target1 = self.add_group()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        user_target2 = self.add_user()
        group_target2 = self.add_group()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup1 = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup1.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup1.id,
            category='pickup',
            membertype='group',
            memberid=group_target1.id,
        )
        call_pickup2 = self.add_pickup()
        self.add_pickup_member(
            pickupid=call_pickup2.id,
            category='member',
            membertype='group',
            memberid=group_interceptor.id,
        )
        self.add_pickup_member(
            pickupid=call_pickup2.id,
            category='pickup',
            membertype='group',
            memberid=group_target2.id,
        )

        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_user_targets,
            contains(contains(empty(), empty())),
        )
        assert_that(
            user_interceptor.users_from_call_pickup_group_interceptors_group_targets,
            contains(contains(
                contains(contains(user_target1)),
                contains(contains(user_target2)),
            )),
        )


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
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        user.schedules = [schedule1, schedule2]

        row = self.session.query(UserFeatures).filter_by(uuid=user.uuid).first()
        assert_that(row, equal_to(user))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        user = self.add_user()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
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

    def test_call_permission_recipients_are_deleted(self):
        user = self.add_user()
        self.add_user_call_permission(user_id=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(CallPermissionAssociation).first()
        assert_that(row, none())

    def test_call_filter_recipients_are_deleted(self):
        user = self.add_user()
        self.add_call_filter_member(bstype='boss', type='user', typeval=str(user.id))

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())

    def test_call_filter_surrogates_are_deleted(self):
        user = self.add_user()
        self.add_call_filter_member(bstype='secretary', type='user', typeval=str(user.id))

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(CallFilterMember).first()
        assert_that(row, none())

    def test_call_pickup_interceptors_are_deleted(self):
        user = self.add_user()
        self.add_pickup_member(category='member', membertype='user', memberid=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())

    def test_call_pickup_targets_are_deleted(self):
        user = self.add_user()
        self.add_pickup_member(category='pickup', membertype='user', memberid=user.id)

        self.session.delete(user)
        self.session.flush()

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())

    def test_schedule_paths_are_deleted(self):
        user = self.add_user()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='user', pathid=user.id)

        self.session.delete(user)
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
