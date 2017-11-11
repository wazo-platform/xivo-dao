# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      equal_to,
                      empty,
                      has_key,
                      has_properties,
                      is_not,
                      not_,
                      none)

from xivo_dao.alchemy.callerid import Callerid
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.queue import Queue
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.schedulepath import SchedulePath

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper


class TestIncalls(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        incall1 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))
        incall2 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))

        assert_that(group.incalls, contains_inanyorder(incall1, incall2))


class TestCallerId(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        callerid = self.add_callerid(type='group', typeval=group.id)

        assert_that(group.caller_id, equal_to(callerid))


class TestFallbacks(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        dialaction = self.add_dialaction(event='key',
                                         category='group',
                                         categoryval=str(group.id))

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

        assert_that(group.fallbacks['key'], has_properties(action='user',
                                                           actionarg1='1'))

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

        assert_that(group.caller_id, has_properties(
            type='group',
            typeval=group.id,
            mode='prepend',
            name=None,
        ))


class TestCallerIdName(DAOTestCase):

    def test_getter(self):
        group = self.add_group(caller_id_name='toto')
        assert_that(group.caller_id_name, equal_to('toto'))

    def test_creator(self):
        group = self.add_group()

        group.caller_id_name = 'toto'
        self.session.flush()

        assert_that(group.caller_id, has_properties(
            type='group',
            typeval=group.id,
            mode=None,
            name='toto',
        ))


class TestSchedules(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        schedule = self.add_schedule()
        self.add_schedule_path(path='group', pathid=group.id, schedule_id=schedule.id)

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))
        assert_that(row.schedules, contains(schedule))

    def test_setter(self):
        group = self.add_group()
        schedule1 = Schedule()
        schedule2 = Schedule()
        group.schedules = [schedule1, schedule2]

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))

        self.session.expire_all()
        assert_that(row.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        group = self.add_group()
        schedule1 = Schedule()
        schedule2 = Schedule()
        group.schedules = [schedule1, schedule2]
        self.session.flush()

        group.schedules = []

        row = self.session.query(Group).filter_by(id=group.id).first()
        assert_that(row, equal_to(group))
        assert_that(row.schedules, empty())

        row = self.session.query(Schedule).first()
        assert_that(row, not_(none()))

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())


class TestCreate(DAOTestCase):

    def test_queue_is_created_with_default_fields(self):
        group = Group(name='groupname')
        self.session.add(group)
        self.session.flush()

        assert_that(group.queue, has_properties(
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
            announce_position='no'
        ))

    def test_queue_is_created_with_all_fields(self):
        group = Group(name='groupname',
                      retry_delay=6,
                      ring_in_use=False,
                      ring_strategy='random',
                      user_timeout=30,
                      music_on_hold='music',
                      enabled=False)
        self.session.add(group)
        self.session.flush()

        assert_that(group.queue, has_properties(
            name='groupname',
            retry=6,
            ring_in_use=False,
            strategy='random',
            timeout=30,
            musicclass='music',
            enabled=False,
        ))


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestDelete, self).setUp()
        self.setup_funckeys()

    def test_schedule_paths_are_deleted(self):
        group = self.add_group()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='group', pathid=group.id)

        self.session.delete(schedule)
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

    def test_group_members_are_deleted(self):
        group = self.add_group()
        self.add_queue_member(queue_name=group.name, category='group')
        self.add_queue_member(queue_name=group.name, category='group')

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())

    def test_funckeys_are_deleted(self):
        group = self.add_group()
        self.add_group_destination(group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(FuncKeyDestGroup).first()
        assert_that(row, none())

    def test_ivr_dialactions_are_deleted(self):
        group = self.add_group()
        self.add_dialaction(category='ivr_choice', action='group', actionarg1=group.id)
        self.add_dialaction(category='ivr', action='group', actionarg1=group.id)

        self.session.delete(group)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
