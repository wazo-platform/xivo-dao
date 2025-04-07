# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import assert_that, contains_inanyorder, equal_to, none
from sqlalchemy.inspection import inspect

from xivo_dao.tests.test_dao import DAOTestCase

from ..application_dest_node import ApplicationDestNode
from ..dialaction import Dialaction


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


class TestLines(DAOTestCase):
    def test_getter(self):
        application = self.add_application()
        line1 = self.add_line(application_uuid=application.uuid)
        line2 = self.add_line(application_uuid=application.uuid)

        assert_that(application.lines, contains_inanyorder(line1, line2))


class TestDeleter(DAOTestCase):
    def test_linefeatures(self):
        application = self.add_application()
        line = self.add_line(application_uuid=application.uuid)

        self.session.delete(application)
        self.session.flush()

        self.session.expire_all()
        assert_that(inspect(application).deleted)
        assert_that(line.application_uuid, equal_to(None))

    def test_dialaction_actions_are_deleted(self):
        application = self.add_application()
        self.add_dialaction(
            category='ivr_choice',
            action='application:custom',
            actionarg1=application.uuid,
        )
        self.add_dialaction(
            category='ivr',
            action='application:custom',
            actionarg1=application.uuid,
        )
        self.add_dialaction(
            category='user',
            action='application:custom',
            actionarg1=application.uuid,
        )
        self.add_dialaction(
            category='incall',
            action='application:custom',
            actionarg1=application.uuid,
        )

        self.session.delete(application)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())
