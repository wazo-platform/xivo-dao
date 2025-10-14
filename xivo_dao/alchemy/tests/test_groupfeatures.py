# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    equal_to,
    has_key,
    has_properties,
    is_not,
    none,
    not_none,
)

from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..callerid import Callerid
from ..dialaction import Dialaction
from ..func_key_dest_group import FuncKeyDestGroup
from ..func_key_dest_group_member import FuncKeyDestGroupMember
from ..groupfeatures import GroupFeatures as Group
from ..pickupmember import PickupMember as CallPickupMember
from ..queue import Queue
from ..queuemember import QueueMember
from ..schedule import Schedule
from ..schedulepath import SchedulePath
from ..userfeatures import UserFeatures


class TestIncalls(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        incall1 = self.add_incall(
            destination=Dialaction(action='group', actionarg1=str(group.id))
        )
        incall2 = self.add_incall(
            destination=Dialaction(action='group', actionarg1=str(group.id))
        )

        assert_that(group.incalls, contains_inanyorder(incall1, incall2))


class TestCallerId(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        callerid = self.add_callerid(type='group', typeval=group.id)

        assert_that(group.caller_id, equal_to(callerid))


class TestFallbacks(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        dialaction = self.add_dialaction(
            event='key', category='group', categoryval=str(group.id)
        )

        assert_that(group.fallbacks['key'], equal_to(dialaction))

    def test_setter(self):
        group = self.add_group()
        dialaction = Dialaction(action='none')

        group.fallbacks = {'key': dialaction}
        self.session.flush()

        assert_that(group.fallbacks['key'], equal_to(dialaction))

    def test_setter_to_none(self):
        group = self.add_group()

        group.fallbacks = {'key': None}
        self.session.flush()

        assert_that(group.fallbacks, empty())

    def test_setter_existing_key(self):
        group = self.add_group()
        dialaction1 = Dialaction(action='none')

        group.fallbacks = {'key': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        group.fallbacks = {'key': dialaction2}
        self.session.flush()

        assert_that(
            group.fallbacks['key'], has_properties(action='user', actionarg1='1')
        )

    def test_setter_delete_undefined_key(self):
        group = self.add_group()
        dialaction1 = Dialaction(action='none')

        group.fallbacks = {'noanswer': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        group.fallbacks = {'busy': dialaction2}
        self.session.flush()

        assert_that(group.fallbacks, is_not(has_key('noanswer')))


class TestCallerIdMode(DAOTestCase):
    def test_getter(self):
        group = self.add_group(caller_id_mode='prepend')
        assert_that(group.caller_id_mode, equal_to('prepend'))

    def test_creator(self):
        group = self.add_group()

        group.caller_id_mode = 'prepend'
        self.session.flush()

        assert_that(
            group.caller_id,
            has_properties(
                type='group',
                typeval=group.id,
                mode='prepend',
                name=None,
            ),
        )


class TestCallerIdName(DAOTestCase):
    def test_getter(self):
        group = self.add_group(caller_id_name='toto')
        assert_that(group.caller_id_name, equal_to('toto'))

    def test_creator(self):
        group = self.add_group()

        group.caller_id_name = 'toto'
        self.session.flush()

        assert_that(
            group.caller_id,
            has_properties(
                type='group',
                typeval=group.id,
                mode=None,
                name='toto',
            ),
        )


class TestSchedules(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        schedule = self.add_schedule()
        self.add_schedule_path(path='group', pathid=group.id, schedule_id=schedule.id)

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))
        assert_that(row.schedules, contains_exactly(schedule))

    def test_setter(self):
        group = self.add_group()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        group.schedules = [schedule1, schedule2]

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        group = self.add_group()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        group.schedules = [schedule1, schedule2]
        self.session.flush()

        group.schedules = []

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))
        assert_that(row.schedules, empty())

        row = self.session.query(Schedule).first()
        assert_that(row, not_none())

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())


class TestUserQueueMembers(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        queue_member1 = self.add_queue_member(
            category='group', usertype='user', queue_name=group.name, position=1
        )
        queue_member2 = self.add_queue_member(
            category='group', usertype='user', queue_name=group.name, position=2
        )

        self.session.expire_all()
        assert_that(
            group.user_queue_members, contains_exactly(queue_member1, queue_member2)
        )

    def test_getter_when_extension_member(self):
        group = self.add_group()
        queue_member = self.add_queue_member(
            category='group', usertype='user', queue_name=group.name, position=1
        )
        self.add_queue_member(
            category='group',
            usertype='user',
            queue_name=group.name,
            interface='Local/12@default',
        )

        self.session.expire_all()
        assert_that(group.user_queue_members, contains_exactly(queue_member))

    def test_setter(self):
        group = self.add_group()
        queue_member = self.add_queue_member(category='group', usertype='user')
        group.user_queue_members = [queue_member]
        self.session.flush()

        self.session.expire_all()
        assert_that(group.user_queue_members, contains_exactly(queue_member))
        assert_that(queue_member.queue_name, equal_to(group.name))

    def test_deleter(self):
        group = self.add_group()
        user = self.add_user()
        self.add_queue_member(
            category='group',
            usertype='user',
            userid=user.id,
            queue_name=group.name,
        )

        group.user_queue_members = []
        self.session.flush()

        self.session.expire_all()
        assert_that(group.user_queue_members, empty())

        row = self.session.query(UserFeatures).first()
        assert_that(row, not_none())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestExtensionQueueMembers(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        queue_member1 = self.add_queue_member(
            category='group',
            usertype='user',
            queue_name=group.name,
            interface='Local/12@default',
            position=1,
        )
        queue_member2 = self.add_queue_member(
            category='group',
            usertype='user',
            queue_name=group.name,
            interface='Local/34@default',
            position=2,
        )

        self.session.expire_all()
        assert_that(
            group.extension_queue_members,
            contains_exactly(queue_member1, queue_member2),
        )

    def test_getter_when_user_member(self):
        group = self.add_group()
        queue_member = self.add_queue_member(
            category='group',
            usertype='user',
            queue_name=group.name,
            interface='Local/12@default',
        )
        self.add_queue_member(
            category='group', usertype='user', queue_name=group.name, position=1
        )

        self.session.expire_all()
        assert_that(group.extension_queue_members, contains_exactly(queue_member))

    def test_setter(self):
        group = self.add_group()
        queue_member = self.add_queue_member(
            category='group', usertype='user', interface='Local/12@default'
        )
        group.user_queue_members = [queue_member]
        self.session.flush()

        self.session.expire_all()
        assert_that(group.extension_queue_members, contains_exactly(queue_member))
        assert_that(queue_member.queue_name, equal_to(group.name))

    def test_deleter(self):
        group = self.add_group()
        user = self.add_user()
        self.add_queue_member(
            category='group',
            usertype='user',
            userid=user.id,
            interface='Local/12@default',
            queue_name=group.name,
        )

        group.extension_queue_members = []
        self.session.flush()

        self.session.expire_all()
        assert_that(group.user_queue_members, empty())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestExten(DAOTestCase):
    def test_getter(self):
        group = self.add_group()
        extension = self.add_extension(type='group', typeval=group.id)

        assert_that(group.exten, equal_to(extension.exten))

    def test_expression(self):
        group = self.add_group()
        extension = self.add_extension(type='group', typeval=group.id)

        result = (
            self.session
            .query(Group)
            .filter(Group.exten == extension.exten)
            .first()
        )  # fmt: skip

        assert_that(result, equal_to(group))
        assert_that(result.exten, equal_to(extension.exten))


class TestCreate(DAOTestCase):
    def test_queue_is_created_with_default_fields(self):
        group = Group(
            name='groupname', label='grouplabel', tenant_uuid=self.default_tenant.uuid
        )
        self.session.add(group)
        self.session.flush()

        assert_that(
            group._queue,
            has_properties(
                name='groupname',
                retry=5,
                ring_in_use=True,
                strategy='ringall',
                timeout=15,
                musicclass=None,
                enabled=True,
                queue_youarenext='queue-youarenext',
                queue_thereare='queue-thereare',
                queue_callswaiting='queue-callswaiting',
                queue_holdtime='queue-holdtime',
                queue_minutes='queue-minutes',
                queue_seconds='queue-seconds',
                queue_thankyou='queue-thankyou',
                queue_reporthold='queue-reporthold',
                periodic_announce='queue-periodic-announce',
                announce_frequency=0,
                periodic_announce_frequency=0,
                announce_round_seconds=0,
                announce_holdtime='no',
                wrapuptime=0,
                maxlen=0,
                memberdelay=0,
                weight=0,
                category='group',
                autofill=1,
                announce_position='no',
            ),
        )

    def test_queue_is_created_with_all_fields(self):
        group = Group(
            tenant_uuid=self.default_tenant.uuid,
            name='groupname',
            label='grouplabel',
            retry_delay=6,
            ring_in_use=False,
            ring_strategy='random',
            user_timeout=30,
            music_on_hold='music',
            enabled=False,
            max_calls=10,
        )
        self.session.add(group)
        self.session.flush()

        assert_that(
            group._queue,
            has_properties(
                name='groupname',
                retry=6,
                ring_in_use=False,
                strategy='random',
                timeout=30,
                musicclass='music',
                enabled=False,
                maxlen=10,
            ),
        )


class TestDelete(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_call_pickup_interceptors_are_deleted(self):
        group = self.add_group()
        self.add_pickup_member(category='member', membertype='group', memberid=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())

    def test_call_pickup_targets_are_deleted(self):
        group = self.add_group()
        self.add_pickup_member(category='pickup', membertype='group', memberid=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(CallPickupMember).first()
        assert_that(row, none())

    def test_schedule_paths_are_deleted(self):
        group = self.add_group()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='group', pathid=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())

    def test_group_dialactions_are_deleted(self):
        group = self.add_group()
        self.add_dialaction(category='group', categoryval=str(group.id))

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())

    def test_queue_is_deleted(self):
        group = self.add_group()

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(Queue).first()
        assert_that(row, none())

    def test_caller_id_is_deleted(self):
        group = self.add_group()
        self.add_callerid(type='group', typeval=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(Callerid).first()
        assert_that(row, none())

    def test_user_queue_members_are_deleted(self):
        group = self.add_group()
        self.add_queue_member(queue_name=group.name, category='group')
        self.add_queue_member(queue_name=group.name, category='group')

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())

    def test_funckeys_group_are_deleted(self):
        group = self.add_group()
        self.add_group_destination(group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(FuncKeyDestGroup).first()
        assert_that(row, none())

    def test_funckeys_group_member_are_deleted(self):
        feature_extension = self.add_feature_extension()
        group = self.add_group()
        self.add_groupmember_destination(group.id, feature_extension.uuid)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(FuncKeyDestGroupMember).first()
        assert_that(row, none())

    def test_dialaction_actions_are_deleted(self):
        group = self.add_group()
        self.add_dialaction(category='ivr_choice', action='group', actionarg1=group.id)
        self.add_dialaction(category='ivr', action='group', actionarg1=group.id)
        self.add_dialaction(category='user', action='group', actionarg1=group.id)
        self.add_dialaction(category='incall', action='group', actionarg1=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())


class TestCallPickupInterceptorPickups(DAOTestCase):
    def test_getter(self):
        group_interceptor = self.add_group()
        user_target = self.add_user()
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
            memberid=user_target.id,
        )

        assert_that(
            group_interceptor.call_pickup_interceptor_pickups,
            contains_exactly(call_pickup),
        )

    def test_two_pickups_two_user_targets(self):
        group_interceptor = self.add_group()
        user_target1 = self.add_user()
        user_target2 = self.add_user()
        call_pickup1 = self.add_pickup()
        call_pickup2 = self.add_pickup()

        call_pickup1.group_interceptors = [group_interceptor]
        call_pickup1.user_targets = [user_target1]

        call_pickup2.group_interceptors = [group_interceptor]
        call_pickup2.user_targets = [user_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            group_interceptor.call_pickup_interceptor_pickups,
            contains_exactly(call_pickup1, call_pickup2),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(
                contains_exactly(user_target1),
                contains_exactly(user_target2),
            ),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(empty(), empty()),
        )

    # Groups
    def test_one_pickup_two_group_targets(self):
        group_interceptor = self.add_group()
        group_target1 = self.add_group()
        user_target1 = self.add_user()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        group_target2 = self.add_group()
        user_target2 = self.add_user()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup = self.add_pickup()

        call_pickup.group_interceptors = [group_interceptor]
        call_pickup.group_targets = [group_target1, group_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            group_interceptor.call_pickup_interceptor_pickups,
            contains_exactly(call_pickup),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(empty()),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(
                contains_exactly(
                    contains_exactly(user_target1), contains_exactly(user_target2)
                )
            ),
        )

    def test_two_pickups_two_group_targets(self):
        group_interceptor = self.add_group()
        group_target1 = self.add_group()
        user_target1 = self.add_user()
        self.add_queue_member(
            queue_name=group_target1.name,
            category='group',
            usertype='user',
            userid=user_target1.id,
        )
        group_target2 = self.add_group()
        user_target2 = self.add_user()
        self.add_queue_member(
            queue_name=group_target2.name,
            category='group',
            usertype='user',
            userid=user_target2.id,
        )
        call_pickup1 = self.add_pickup()
        call_pickup1.group_interceptors = [group_interceptor]
        call_pickup1.group_targets = [group_target1]

        call_pickup2 = self.add_pickup()
        call_pickup2.group_interceptors = [group_interceptor]
        call_pickup2.group_targets = [group_target2]
        self.session.flush()

        self.session.expire_all()
        assert_that(
            group_interceptor.call_pickup_interceptor_pickups,
            contains_exactly(call_pickup1, call_pickup2),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(empty(), empty()),
        )

        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(
                contains_exactly(contains_exactly(user_target1)),
                contains_exactly(contains_exactly(user_target2)),
            ),
        )


class TestUsersFromCallPickupUserTargets(DAOTestCase):
    def test_one_pickup_two_user_targets(self):
        group_interceptor = self.add_group()
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
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(contains_exactly(user_target1, user_target2)),
        )
        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(empty()),
        )

    def test_two_pickups_two_user_targets(self):
        group_interceptor = self.add_group()
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
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(
                contains_exactly(user_target1), contains_exactly(user_target2)
            ),
        )
        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(empty(), empty()),
        )


class TestUsersFromCallPickupGroupTargets(DAOTestCase):
    def test_one_pickup_two_user_targets(self):
        group_interceptor = self.add_group()
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
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(empty()),
        )
        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(
                contains_exactly(
                    contains_exactly(user_target1), contains_exactly(user_target2)
                )
            ),
        )

    def test_two_pickups_two_user_targets(self):
        group_interceptor = self.add_group()
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
            group_interceptor.users_from_call_pickup_user_targets,
            contains_exactly(empty(), empty()),
        )
        assert_that(
            group_interceptor.users_from_call_pickup_group_targets,
            contains_exactly(
                contains_exactly(contains_exactly(user_target1)),
                contains_exactly(contains_exactly(user_target2)),
            ),
        )
