# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_properties,
    none,
)

from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..dialaction import Dialaction
from ..func_key_dest_queue import FuncKeyDestQueue
from ..queue import Queue
from ..queuefeatures import QueueFeatures
from ..queuemember import QueueMember
from ..schedulepath import SchedulePath


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
        assert_that(queue.caller_id, has_properties(
            type='queue',
            typeval=queue.id,
            mode='prepend',
            name=None,
        ))


class TestCallerIdName(DAOTestCase):

    def test_getter(self):
        queue = self.add_queuefeatures(caller_id_name='toto')
        assert_that(queue.caller_id_name, equal_to('toto'))

    def test_creator(self):
        queue = self.add_queuefeatures()

        queue.caller_id_name = 'toto'
        self.session.flush()

        assert_that(queue.caller_id, has_properties(
            type='queue',
            typeval=queue.id,
            mode=None,
            name='toto',
        ))


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
        queue = QueueFeatures(name='queuename', displayname='')
        self.session.add(queue)
        self.session.flush()

        self.session.expire_all()
        assert_that(queue._queue, has_properties(
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
        ))

    def test_metaqueue_is_created_with_all_fields(self):
        queue = QueueFeatures(name='queuename', enabled=False, displayname='')
        self.session.add(queue)
        self.session.flush()

        assert_that(queue._queue, has_properties(
            name='queuename',
            enabled=False,
        ))


class TestExtensions(DAOTestCase):

    def test_getter(self):
        queue = self.add_queuefeatures()
        extension = self.add_extension(type='queue', typeval=str(queue.id))

        self.session.expire_all()
        assert_that(queue.extensions, contains(extension))


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super(TestDelete, self).setUp()
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

    def test_ivr_dialactions_are_deleted(self):
        queue = self.add_queuefeatures()
        self.add_dialaction(category='ivr_choice', action='queue', actionarg1=queue.id)
        self.add_dialaction(category='ivr', action='queue', actionarg1=queue.id)

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
