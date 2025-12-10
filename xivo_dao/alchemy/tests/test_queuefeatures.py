# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
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

from ..agentfeatures import AgentFeatures
from ..dialaction import Dialaction
from ..func_key_dest_queue import FuncKeyDestQueue
from ..queue import Queue
from ..queuefeatures import QueueFeatures
from ..queuemember import QueueMember
from ..schedule import Schedule
from ..schedulepath import SchedulePath
from ..userfeatures import UserFeatures


class TestCallerId(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        callerid = self.add_callerid(type='queue', typeval=queue.id)

        self.session.expire_all()
        assert_that(queue.caller_id, equal_to(callerid))


class TestCallerIdMode(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures(caller_id_mode='prepend')

        self.session.expire_all()
        assert_that(queue.caller_id_mode, equal_to('prepend'))

    def test_creator(self):
        queue = self.add_queuefeatures()

        queue.caller_id_mode = 'prepend'
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue.caller_id,
            has_properties(
                type='queue',
                typeval=queue.id,
                mode='prepend',
                name=None,
            ),
        )


class TestCallerIdName(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures(caller_id_name='toto')
        assert_that(queue.caller_id_name, equal_to('toto'))

    def test_creator(self):
        queue = self.add_queuefeatures()

        queue.caller_id_name = 'toto'
        self.session.flush()

        assert_that(
            queue.caller_id,
            has_properties(
                type='queue',
                typeval=queue.id,
                mode=None,
                name='toto',
            ),
        )


class TestFallbacks(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        dialaction = self.add_dialaction(
            event='busy', category='queue', categoryval=str(queue.id)
        )

        assert_that(queue.fallbacks['busy'], equal_to(dialaction))

    def test_setter(self):
        queue = self.add_queuefeatures()
        dialaction = Dialaction(action='none')

        queue.fallbacks = {'busy': dialaction}
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue.fallbacks['busy'],
            has_properties(action='none', category='queue', event='busy'),
        )

    def test_setter_to_none(self):
        queue = self.add_queuefeatures()

        queue.fallbacks = {'busy': None}
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.fallbacks, empty())

    def test_setter_existing_key(self):
        queue = self.add_queuefeatures()
        dialaction1 = Dialaction(action='none')

        queue.fallbacks = {'busy': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        queue.fallbacks = {'busy': dialaction2}
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue.fallbacks['busy'], has_properties(action='user', actionarg1='1')
        )

    def test_setter_delete_undefined_key(self):
        queue = self.add_queuefeatures()
        dialaction1 = Dialaction(action='none')

        queue.fallbacks = {'noanswer': dialaction1}
        self.session.flush()
        self.session.expire_all()

        dialaction2 = Dialaction(action='user', actionarg1='1')
        queue.fallbacks = {'busy': dialaction2}
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.fallbacks, is_not(has_key('noanswer')))


class TestWaitTimeDestination(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        dialaction = self.add_dialaction(
            event='qwaittime', category='queue', categoryval=str(queue.id)
        )

        assert_that(queue.wait_time_destination, equal_to(dialaction))

    def test_setter(self):
        queue = self.add_queuefeatures()
        dialaction = Dialaction(action='none')

        queue.wait_time_destination = dialaction
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue.wait_time_destination,
            has_properties(action='none', category='queue', event='qwaittime'),
        )

    def test_setter_to_none(self):
        queue = self.add_queuefeatures()

        queue.wait_time_destination = None
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.wait_time_destination, equal_to(None))

        result = self.session.get(Dialaction, ('qwaittime', 'queue', queue.id))
        assert_that(result, equal_to(None))


class TestWaitRatioDestination(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        dialaction = self.add_dialaction(
            event='qwaitratio', category='queue', categoryval=str(queue.id)
        )

        assert_that(queue.wait_ratio_destination, equal_to(dialaction))

    def test_setter(self):
        queue = self.add_queuefeatures()
        dialaction = Dialaction(action='none')

        queue.wait_ratio_destination = dialaction
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue.wait_ratio_destination,
            has_properties(action='none', category='queue', event='qwaitratio'),
        )

    def test_setter_to_none(self):
        queue = self.add_queuefeatures()

        queue.wait_ratio_destination = None
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.wait_ratio_destination, equal_to(None))

        result = self.session.get(Dialaction, ('qwaitratio', 'queue', queue.id))
        assert_that(result, equal_to(None))


class TestUserQueueMembers(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        queue_member1 = self.add_queue_member(
            category='queue', usertype='user', queue_name=queue.name, position=1
        )
        queue_member2 = self.add_queue_member(
            category='queue', usertype='user', queue_name=queue.name, position=2
        )

        self.session.expire_all()
        assert_that(
            queue.user_queue_members, contains_exactly(queue_member1, queue_member2)
        )

    def test_setter(self):
        queue = self.add_queuefeatures()
        queue_member = self.add_queue_member(category='queue', usertype='user')
        queue.user_queue_members = [queue_member]
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.user_queue_members, contains_exactly(queue_member))
        assert_that(queue_member.queue_name, equal_to(queue.name))

    def test_deleter(self):
        queue = self.add_queuefeatures()
        user = self.add_user()
        self.add_queue_member(
            category='queue',
            usertype='user',
            userid=user.id,
            queue_name=queue.name,
        )

        queue.user_queue_members = []
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.user_queue_members, empty())

        row = self.session.query(UserFeatures).first()
        assert_that(row, not_none())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestAgentQueueMembers(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        queue_member1 = self.add_queue_member(
            category='queue', usertype='agent', queue_name=queue.name, position=1
        )
        queue_member2 = self.add_queue_member(
            category='queue', usertype='agent', queue_name=queue.name, position=2
        )

        self.session.expire_all()
        assert_that(
            queue.agent_queue_members, contains_exactly(queue_member1, queue_member2)
        )

    def test_setter(self):
        queue = self.add_queuefeatures()
        queue_member = self.add_queue_member(category='queue', usertype='agent')
        queue.user_queue_members = [queue_member]
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.agent_queue_members, contains_exactly(queue_member))
        assert_that(queue_member.queue_name, equal_to(queue.name))

    def test_deleter(self):
        queue = self.add_queuefeatures()
        agent = self.add_agent()
        self.add_queue_member(
            category='queue',
            usertype='agent',
            userid=agent.id,
            queue_name=queue.name,
        )

        queue.agent_queue_members = []
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.agent_queue_members, empty())

        row = self.session.query(AgentFeatures).first()
        assert_that(row, not_none())

        row = self.session.query(QueueMember).first()
        assert_that(row, none())


class TestSchedules(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()
        self.add_schedule_path(path='queue', pathid=queue.id, schedule_id=schedule.id)

        self.session.expire_all()
        assert_that(queue.schedules, contains_exactly(schedule))

    def test_setter(self):
        queue = self.add_queuefeatures()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        queue.schedules = [schedule1, schedule2]
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.schedules, contains_inanyorder(schedule1, schedule2))

    def test_deleter(self):
        queue = self.add_queuefeatures()
        schedule1 = self.add_schedule()
        schedule2 = self.add_schedule()
        queue.schedules = [schedule1, schedule2]
        self.session.flush()

        queue.schedules = []
        self.session.flush()

        self.session.expire_all()
        assert_that(queue.schedules, empty())

        row = self.session.query(Schedule).first()
        assert_that(row, not_none())

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())


class TestLabel(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(displayname='toto')
        assert_that(queue.label, equal_to('toto'))

    def test_getter_none(self):
        queue = QueueFeatures(displayname='')
        assert_that(queue.label, equal_to(None))

    def test_setter(self):
        queue = QueueFeatures(label='toto')
        assert_that(queue.displayname, equal_to('toto'))

    def test_setter_none(self):
        queue = QueueFeatures(label=None)
        assert_that(queue.displayname, equal_to(''))


class TestDataQualityBool(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(data_quality=1)
        assert_that(queue.data_quality_bool, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(data_quality_bool=True)
        assert_that(queue.data_quality, equal_to(1))


class TestIgnoreForwardBool(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(ignore_forward=1)
        assert_that(queue.ignore_forward_bool, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(ignore_forward_bool=True)
        assert_that(queue.ignore_forward, equal_to(1))


class TestDTMFHangupCalleeEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(hitting_callee=1)
        assert_that(queue.dtmf_hangup_callee_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_hangup_callee_enabled=True)
        assert_that(queue.hitting_callee, equal_to(1))


class TestDTMFHangupCallerEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(hitting_caller=1)
        assert_that(queue.dtmf_hangup_caller_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_hangup_caller_enabled=True)
        assert_that(queue.hitting_caller, equal_to(1))


class TestDTMFTransferCalleeEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(transfer_user=1)
        assert_that(queue.dtmf_transfer_callee_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_transfer_callee_enabled=True)
        assert_that(queue.transfer_user, equal_to(1))


class TestDTMFTransferCallerEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(transfer_call=1)
        assert_that(queue.dtmf_transfer_caller_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_transfer_caller_enabled=True)
        assert_that(queue.transfer_call, equal_to(1))


class TestDTMFRecordCalleeEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(write_caller=1)
        assert_that(queue.dtmf_record_callee_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_record_callee_enabled=True)
        assert_that(queue.write_caller, equal_to(1))


class TestDTMFRecordCallerEnabled(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(write_calling=1)
        assert_that(queue.dtmf_record_caller_enabled, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(dtmf_record_caller_enabled=True)
        assert_that(queue.write_calling, equal_to(1))


class TestRetryOnTimeout(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(retries=1)
        assert_that(queue.retry_on_timeout, equal_to(False))

    def test_setter(self):
        queue = QueueFeatures(retry_on_timeout=False)
        assert_that(queue.retries, equal_to(1))


class TestRingOnHold(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(ring=1)
        assert_that(queue.ring_on_hold, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(ring_on_hold=True)
        assert_that(queue.ring, equal_to(1))


class TestAnnounceHoldTimeOnEntry(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(announce_holdtime=1)
        assert_that(queue.announce_hold_time_on_entry, equal_to(True))

    def test_setter(self):
        queue = QueueFeatures(announce_hold_time_on_entry=True)
        assert_that(queue.announce_holdtime, equal_to(1))


class TestWaitTimeThreshold(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(waittime=1234)
        assert_that(queue.wait_time_threshold, equal_to(1234))

    def test_setter(self):
        queue = QueueFeatures(wait_time_threshold=1234)
        assert_that(queue.waittime, equal_to(1234))


class TestWaitRatioThreshold(DAOTestCase):
    def test_getter(self):
        queue = QueueFeatures(waitratio=12.34)
        assert_that(queue.wait_ratio_threshold, equal_to(12.34))

    def test_setter(self):
        queue = QueueFeatures(wait_ratio_threshold=12.34)
        assert_that(queue.waitratio, equal_to(12.34))


class TestCreate(DAOTestCase):
    def test_metaqueue_is_created_with_default_fields(self):
        queue = QueueFeatures(
            tenant_uuid=self.default_tenant.uuid,
            name='queuename',
            displayname='',
        )
        self.session.add(queue)
        self.session.flush()

        self.session.expire_all()
        assert_that(
            queue._queue,
            has_properties(
                name='queuename',
                category='queue',
                timeout=15,
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
                retry=5,
                wrapuptime=0,
                maxlen=0,
                servicelevel=0,
                strategy='ringall',
                memberdelay=0,
                weight=0,
                timeoutpriority='conf',
                setqueueentryvar=1,
                setqueuevar=1,
            ),
        )

    def test_metaqueue_is_created_with_all_fields(self):
        queue = QueueFeatures(
            tenant_uuid=self.default_tenant.uuid,
            name='queuename',
            enabled=False,
            displayname='',
            music_on_hold='music_on_hold',
        )
        self.session.add(queue)
        self.session.flush()

        assert_that(
            queue._queue,
            has_properties(
                name='queuename',
                enabled=False,
                musicclass='music_on_hold',
            ),
        )


class TestExtensions(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=str(queue.id))

        self.session.expire_all()
        assert_that(queue.extensions, contains_exactly(extension))


class TestExten(DAOTestCase):
    def test_getter(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=queue.id)

        assert_that(queue.exten, equal_to(extension.exten))

    def test_expression(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=queue.id)

        result = (
            self.session.query(QueueFeatures)
            .filter(QueueFeatures.exten == extension.exten)
            .first()
        )

        assert_that(result, equal_to(queue))
        assert_that(result.exten, equal_to(extension.exten))


class TestDelete(DAOTestCase, FuncKeyHelper):
    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_queue_is_deleted(self):
        queue = self.add_queuefeatures()

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(Queue).first()
        assert_that(row, none())

    def test_funckeys_are_deleted(self):
        queue = self.add_queuefeatures()
        self.add_queue_destination(queue.id)

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(FuncKeyDestQueue).first()
        assert_that(row, none())

    def test_queue_dialactions_are_deleted(self):
        queue = self.add_queuefeatures()
        self.add_dialaction(category='queue', categoryval=str(queue.id))

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())

    def test_dialaction_actions_are_deleted(self):
        queue = self.add_queuefeatures()
        self.add_dialaction(category='ivr_choice', action='queue', actionarg1=queue.id)
        self.add_dialaction(category='ivr', action='queue', actionarg1=queue.id)
        self.add_dialaction(category='user', action='queue', actionarg1=queue.id)
        self.add_dialaction(category='incall', action='queue', actionarg1=queue.id)

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())

    def test_queue_members_are_deleted(self):
        queue = self.add_queuefeatures()
        self.add_queue_member(queue_name=queue.name, category='queue')
        self.add_queue_member(queue_name=queue.name, category='queue')

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(QueueMember).first()
        assert_that(row, none())

    def test_schedule_paths_are_deleted(self):
        queue = self.add_queuefeatures()
        schedule = self.add_schedule()
        self.add_schedule_path(schedule_id=schedule.id, path='queue', pathid=queue.id)

        self.session.delete(queue)
        self.session.flush()

        row = self.session.query(SchedulePath).first()
        assert_that(row, none())
