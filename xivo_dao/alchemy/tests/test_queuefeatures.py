# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    has_properties,
    none,
)

from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..func_key_dest_queue import FuncKeyDestQueue
from ..queue import Queue
from ..queuefeatures import QueueFeatures


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
