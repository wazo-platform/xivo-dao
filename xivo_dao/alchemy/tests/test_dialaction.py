# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.tests.test_dao import DAOTestCase


class TestGoSubArgs(unittest.TestCase):

    def test_getter(self):
        dialaction = Dialaction(action='extension',
                                actionarg1='21',
                                actionarg2='foobar',
                                linked=1)

        assert_that(dialaction.gosub_args, equal_to('extension,21,foobar'))

    def test_getter_with_none(self):
        dialaction = Dialaction(action='none', linked=1)

        assert_that(dialaction.gosub_args, equal_to('none,,'))

    def test_getter_with_unlinked_dialaction(self):
        dialaction = Dialaction(action='user', actionarg1='1', linked=0)

        assert_that(dialaction.gosub_args, equal_to('none'))


class TestType(unittest.TestCase):

    def test_getter_when_subtype(self):
        dialaction = Dialaction(action='application:disa')

        assert_that(dialaction.type, equal_to('application'))

    def test_getter_when_no_subtype(self):
        dialaction = Dialaction(action='extension')

        assert_that(dialaction.type, equal_to('extension'))

    def test_getter_when_none(self):
        dialaction = Dialaction(action=None)

        assert_that(dialaction.type, equal_to(None))

    def test_setter_when_no_action(self):
        dialaction = Dialaction(action=None)

        dialaction.type = 'hangup'

        assert_that(dialaction.action, equal_to('hangup'))

    def test_setter_when_subtype(self):
        dialaction = Dialaction(action='application:disa')

        dialaction.type = 'hangup'

        assert_that(dialaction.action, equal_to('hangup:disa'))

    def test_setter_when_no_subtype(self):
        dialaction = Dialaction(action='extension')

        dialaction.type = 'hangup'

        assert_that(dialaction.action, equal_to('hangup'))


class TestSubtype(unittest.TestCase):

    def test_getter(self):
        dialaction = Dialaction(action='application:disa')

        assert_that(dialaction.subtype, equal_to('disa'))

    def test_getter_when_no_subtype(self):
        dialaction = Dialaction(action='extension')

        assert_that(dialaction.subtype, equal_to(None))

    def test_getter_when_no_action(self):
        dialaction = Dialaction(action=None)

        assert_that(dialaction.subtype, equal_to(None))

    def test_setter(self):
        dialaction = Dialaction(action='application:callbackdisa')

        dialaction.subtype = 'disa'

        assert_that(dialaction.action, equal_to('application:disa'))


class TestIncall(DAOTestCase):

    def test_getter(self):
        dialaction = self.add_dialaction()
        incall = self.add_incall(destination=dialaction)

        assert_that(dialaction.incall, equal_to(incall))


class TestVoicemail(DAOTestCase):

    def test_getter(self):
        voicemail = self.add_voicemail()
        dialaction = self.add_dialaction(action='voicemail', actionarg1=voicemail.id)

        assert_that(dialaction.voicemail, equal_to(voicemail))


class TestIvr(DAOTestCase):

    def test_getter(self):
        ivr = self.add_ivr()
        dialaction = self.add_dialaction(action='ivr', actionarg1=ivr.id)

        assert_that(dialaction.ivr, equal_to(ivr))


class TestGroup(DAOTestCase):

    def test_getter(self):
        group = self.add_group()
        dialaction = self.add_dialaction(action='group', actionarg1=group.id)

        assert_that(dialaction.group, equal_to(group))


class TestUser(DAOTestCase):

    def test_getter(self):
        user = self.add_user()
        dialaction = self.add_dialaction(action='user', actionarg1=user.id)

        assert_that(dialaction.user, equal_to(user))
