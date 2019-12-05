# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, equal_to, none

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr import IVR
from xivo_dao.alchemy.ivr_choice import IVRChoice
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

    def test_setter_none(self):
        dialaction = Dialaction(action='application:disa')
        dialaction.subtype = None
        assert_that(dialaction.action, equal_to('application'))


class TestIncall(DAOTestCase):

    def test_getter(self):
        dialaction = self.add_dialaction()
        incall = self.add_incall(destination=dialaction)

        assert_that(dialaction.incall, equal_to(incall))

    def test_getter_when_destination_deleted(self):
        ivr = self.add_ivr()
        user = self.add_user()
        dialaction = self.add_dialaction(action='ivr', actionarg1=ivr.id)

        incall = self.add_incall(destination=dialaction)
        assert_that(incall.destination.linked, equal_to(1))
        assert_that(incall.destination.ivr, equal_to(ivr))

        incall.destination.linked = 0
        self.session.delete(ivr)
        self.session.add(incall)
        self.session.flush()
        assert_that(incall.destination.linked, equal_to(0))

        dialaction = Dialaction(action='user', actionarg1=user.id)
        incall.destination = dialaction
        self.session.merge(incall)
        self.session.flush()

        assert_that(incall.destination.linked, equal_to(1))
        assert_that(incall.destination.user, equal_to(user))


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


class TestConference(DAOTestCase):

    def test_getter(self):
        conference = self.add_conference()
        dialaction = self.add_dialaction(action='conference', actionarg1=conference.id)

        assert_that(dialaction.conference, equal_to(conference))


class TestIVRChoice(DAOTestCase):

    def test_getter(self):
        ivr = self.add_ivr()
        ivr_choice = self.add_ivr_choice(ivr_id=ivr.id)
        dialaction = self.add_dialaction(category='ivr_choice', categoryval=ivr_choice.id)

        assert_that(dialaction.ivr_choice, equal_to(ivr_choice))


class TestApplication(DAOTestCase):

    def test_getter(self):
        application = self.add_application()
        dialaction = self.add_dialaction(action='application:custom', actionarg1=application.uuid)

        assert_that(dialaction.application, equal_to(application))


class TestQueue(DAOTestCase):

    def test_getter(self):
        queue = self.add_queuefeatures()
        dialaction = self.add_dialaction(action='queue', actionarg1=queue.id)

        assert_that(dialaction.queue, equal_to(queue))


class TestDelete(DAOTestCase):

    def test_ivr_choice_are_deleted(self):
        ivr = self.add_ivr()
        ivr_choice = self.add_ivr_choice(ivr_id=ivr.id)
        dialaction = self.add_dialaction(category='ivr_choice', categoryval=str(ivr_choice.id))

        self.session.delete(dialaction)
        self.session.flush()

        row = self.session.query(IVRChoice).first()
        assert_that(row, none())

        row = self.session.query(IVR).first()
        assert_that(row, equal_to(ivr))
