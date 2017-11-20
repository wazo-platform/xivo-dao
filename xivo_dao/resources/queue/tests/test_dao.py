# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to

from xivo_dao.tests.test_dao import DAOTestCase
from xivo_dao.resources.queue import dao as queue_dao


class TestQueueExist(DAOTestCase):

    def test_given_no_queue_then_returns_false(self):
        result = queue_dao.exists(1)

        assert_that(result, equal_to(False))

    def test_given_queue_exists_then_return_true(self):
        queue_row = self.add_queuefeatures()

        result = queue_dao.exists(queue_row.id)

        assert_that(result, equal_to(True))


class TestFindBy(DAOTestCase):

    def test_find_by_name(self):
        queue_row = self.add_queuefeatures(name='myname')

        queue = queue_dao.find_by(name='myname')

        assert_that(queue, equal_to(queue_row))
        assert_that(queue.name, equal_to('myname'))
