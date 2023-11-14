# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    none,
)

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.resources.func_key.tests.test_helpers import FuncKeyHelper
from xivo_dao.tests.test_dao import DAOTestCase

from ..conference import Conference
from ..func_key_dest_conference import FuncKeyDestConference


class TestIncalls(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        incall1 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))
        incall2 = self.add_incall(destination=Dialaction(action='group',
                                                         actionarg1=str(group.id)))

        assert_that(group.incalls, contains_inanyorder(incall1, incall2))


class TestExten(DAOTestCase):

    def test_getter(self):
        conference = self.add_conference()
        extension = self.add_extension(type='conference', typeval=conference.id)

        assert_that(conference.exten, equal_to(extension.exten))

    def test_expression(self):
        conference = self.add_conference()
        extension = self.add_extension(type='conference', typeval=conference.id)

        result = (
            self.session.query(Conference)
            .filter(Conference.exten == extension.exten)
            .first()
        )

        assert_that(result, equal_to(conference))
        assert_that(result.exten, equal_to(extension.exten))


class TestDelete(DAOTestCase, FuncKeyHelper):

    def setUp(self):
        super().setUp()
        self.setup_funckeys()

    def test_dialaction_actions_are_deleted(self):
        conference = self.add_conference()
        self.add_dialaction(category='ivr_choice', action='conference', actionarg1=conference.id)
        self.add_dialaction(category='ivr', action='conference', actionarg1=conference.id)
        self.add_dialaction(category='user', action='conference', actionarg1=conference.id)
        self.add_dialaction(category='incall', action='conference', actionarg1=conference.id)

        self.session.delete(conference)
        self.session.flush()

        row = self.session.query(Dialaction).first()
        assert_that(row, none())

    def test_funckeys_conference_are_deleted(self):
        conference = self.add_conference()
        self.add_conference_destination(conference.id)

        self.session.delete(conference)
        self.session.flush()

        row = self.session.query(FuncKeyDestConference).first()
        assert_that(row, none())
