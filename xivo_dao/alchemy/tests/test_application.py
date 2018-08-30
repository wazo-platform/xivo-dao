# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import (
    assert_that,
    equal_to,
)
from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..application_dest_node import ApplicationDestNode


class TestDestNode(DAOTestCase):

    def test_dest_node_create(self):
        application = self.add_application()
        dest_node = ApplicationDestNode(type_='holding')

        application.dest_node = dest_node
        self.session.flush()

        self.session.expire_all()
        assert_that(inspect(dest_node).persistent)
        assert_that(application.dest_node, equal_to(dest_node))

    def test_dest_node_dissociate(self):
        application = self.add_application()
        dest_node = self.add_application_dest_node(application_uuid=application.uuid)

        application.dest_node = None
        self.session.flush()

        self.session.expire_all()
        assert_that(inspect(dest_node).deleted)
        assert_that(application.dest_node, equal_to(None))
